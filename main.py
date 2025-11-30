from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import io
import logging
import time
from typing import Optional
from enum import Enum
import sys

# Production Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
ALLOWED_ORIGINS = ["*"]  # Update with your frontend domains in production

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Lazy import to catch compatibility issues
remove = None

def get_remove_function():
    global remove
    if remove is None:
        try:
            from backgroundremover.bg import remove as bg_remove
            remove = bg_remove
        except Exception as e:
            raise RuntimeError(
                f"Failed to import backgroundremover. "
                f"Python 3.13 has compatibility issues. Please use Python 3.10-3.11. Error: {e}"
            )
    return remove

app = FastAPI(
    title="Background Remover API",
    description="Production-ready API for removing backgrounds from images using AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware - Configure for your domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security: Trusted Host Middleware
# Uncomment and configure for production:
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
# )

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
    return response


class ModelChoice(str, Enum):
    u2net = "u2net"
    u2net_human_seg = "u2net_human_seg"
    u2netp = "u2netp"


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Background Remover API",
        "endpoints": {
            "POST /remove-background": "Upload an image to remove its background",
            "GET /health": "Health check endpoint"
        },
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    try:
        # Test if backgroundremover can be imported
        get_remove_function()
        return {
            "status": "healthy",
            "service": "background-remover-api",
            "version": "1.0.0",
            "python_version": sys.version.split()[0]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.post("/remove-background")
async def remove_background(
    file: UploadFile = File(..., description="Image file to process"),
    model: ModelChoice = Query(
        ModelChoice.u2net,
        description="AI model to use for background removal"
    ),
    alpha_matting: bool = Query(
        False,
        description="⚠️ DISABLED: Alpha matting not compatible with Python 3.13. Use Python 3.10-3.11 for this feature."
    ),
    alpha_matting_foreground_threshold: int = Query(
        240,
        ge=0,
        le=255,
        description="Foreground threshold for alpha matting (disabled in Python 3.13)"
    ),
    alpha_matting_background_threshold: int = Query(
        10,
        ge=0,
        le=255,
        description="Background threshold for alpha matting (disabled in Python 3.13)"
    ),
    alpha_matting_erode_size: int = Query(
        10,
        ge=1,
        le=50,
        description="Erosion size for alpha matting (disabled in Python 3.13)"
    ),
    only_mask: bool = Query(
        False,
        description="Return only the binary mask instead of the processed image"
    ),
    background_color: Optional[str] = Query(
        None,
        description="Replace background with custom RGB color (format: '255,0,0')"
    )
):
    """
    Remove background from an uploaded image
    
    - **file**: Image file (JPG, PNG, HEIC, HEIF)
    - **model**: Choose AI model (u2net for general, u2net_human_seg for people, u2netp for faster processing)
    - **alpha_matting**: Enable for refined edges
    - **only_mask**: Return grayscale mask instead of transparent PNG
    - **background_color**: Replace with solid color (e.g., '255,0,0' for red)
    
    Returns: PNG image with transparent background (or custom background)
    """
    
    # Validate file type
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.heic', '.heif'}
    file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        logger.warning(f"Invalid file type attempted: {file_ext}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Read file and validate size
    image_data = await file.read()
    file_size = len(image_data)
    
    if file_size > MAX_FILE_SIZE:
        logger.warning(f"File too large: {file_size / 1024 / 1024:.2f}MB")
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    logger.info(f"Processing {file.filename} ({file_size / 1024:.2f}KB) with model {model.value}")
    
    try:
        # Get the remove function
        remove_func = get_remove_function()
        
        # Parse background color if provided
        bg_color = None
        if background_color:
            try:
                rgb_values = tuple(int(x.strip()) for x in background_color.split(','))
                if len(rgb_values) != 3 or not all(0 <= v <= 255 for v in rgb_values):
                    raise ValueError("RGB values must be between 0 and 255")
                bg_color = rgb_values
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid background_color format. Use 'R,G,B' (e.g., '255,0,0'). Error: {str(e)}"
                )
        
        # Force disable alpha_matting for Python 3.13 compatibility
        if alpha_matting:
            raise HTTPException(
                status_code=400,
                detail="Alpha matting is not compatible with Python 3.13. Please use Python 3.10-3.11, or set alpha_matting=false."
            )
        
        # Process the image with backgroundremover
        processed_image = remove_func(
            image_data,
            model_name=model.value,
            alpha_matting=False,  # Force disabled for Python 3.13
            alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
            alpha_matting_background_threshold=alpha_matting_background_threshold,
            alpha_matting_erode_structure_size=alpha_matting_erode_size,
            only_mask=only_mask,
            background_color=bg_color
        )
        
        # Return the processed image
        return StreamingResponse(
            io.BytesIO(processed_image),
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename=processed_{file.filename.rsplit('.', 1)[0]}.png"
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )


@app.post("/remove-background-simple")
async def remove_background_simple(file: UploadFile = File(...)):
    """
    Simplified endpoint - just upload an image and get back transparent background
    
    Uses default settings with u2net model
    """
    
    try:
        remove_func = get_remove_function()
        image_data = await file.read()
        
        # Validate file size
        if len(image_data) > MAX_FILE_SIZE:
            logger.warning(f"File too large: {len(image_data) / 1024 / 1024:.2f}MB")
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        logger.info(f"Processing {file.filename} with u2net model")
        processed_image = remove_func(image_data, model_name="u2net")
        
        return StreamingResponse(
            io.BytesIO(processed_image),
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename=no_bg_{file.filename.rsplit('.', 1)[0]}.png"
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Background Remover API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
