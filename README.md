# Background Remover API

A FastAPI-based REST API for removing backgrounds from images using AI (powered by the popular [backgroundremover](https://github.com/nadermx/backgroundremover) library).

## Features

- 🎨 Remove backgrounds from images using state-of-the-art AI models
- 🚀 Fast and easy-to-use REST API
- 🎯 Multiple AI models to choose from (u2net, u2net_human_seg, u2netp)
- 🔧 Customizable processing options:
  - Alpha matting for better edge quality
  - Custom background colors
  - Binary mask output
  - Adjustable edge sharpness
- 📝 Automatic interactive API documentation (Swagger UI)
- 🖼️ Supports JPG, PNG, HEIC, and HEIF formats

## Installation

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

**Note:** The first time you run the API, it will automatically download the AI models (~176MB for u2net).

### 2. (Optional) Install PyTorch with CUDA for GPU acceleration

For much faster processing (5-10x speedup), install PyTorch with CUDA support:

```bash
# For CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

## Usage

### Start the server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Simple Background Removal (POST /remove-background-simple)

Upload an image and get back a transparent PNG with default settings.

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/remove-background-simple" \
  -F "file=@your_image.jpg" \
  -o output.png
```

**Example using Python:**
```python
import requests

with open("input.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/remove-background-simple",
        files={"file": f}
    )

with open("output.png", "wb") as f:
    f.write(response.content)
```

### 2. Advanced Background Removal (POST /remove-background)

Full control over processing parameters.

**Parameters:**
- `file` (required): Image file to process
- `model`: AI model choice
  - `u2net` (default): Best for general objects
  - `u2net_human_seg`: Best for people/portraits
  - `u2netp`: Faster but slightly lower quality
- `alpha_matting`: Enable for better edge quality (default: false)
- `alpha_matting_erode_size`: Edge sharpness (1-5=sharp, 15-25=soft, default: 10)
- `only_mask`: Return grayscale mask instead of transparent image
- `background_color`: Replace with solid color (format: "R,G,B", e.g., "255,0,0" for red)

**Example - Remove background from portrait:**
```bash
curl -X POST "http://localhost:8000/remove-background?model=u2net_human_seg&alpha_matting=true" \
  -F "file=@portrait.jpg" \
  -o output.png
```

**Example - Replace background with custom color:**
```bash
curl -X POST "http://localhost:8000/remove-background?background_color=0,255,0" \
  -F "file=@image.jpg" \
  -o output_green_bg.png
```

**Example - Get only the mask:**
```bash
curl -X POST "http://localhost:8000/remove-background?only_mask=true" \
  -F "file=@image.jpg" \
  -o mask.png
```

**Example using Python with custom options:**
```python
import requests

with open("input.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/remove-background",
        files={"file": f},
        params={
            "model": "u2net_human_seg",
            "alpha_matting": True,
            "alpha_matting_erode_size": 5,  # Sharper edges
            "background_color": "255,255,255"  # White background
        }
    )

with open("output.png", "wb") as f:
    f.write(response.content)
```

### 3. Health Check (GET /health)

Check if the API is running.

```bash
curl http://localhost:8000/health
```

## Testing the API

You can test the API using the built-in Swagger UI:

1. Start the server: `python main.py`
2. Open browser: http://localhost:8000/docs
3. Click on "POST /remove-background-simple"
4. Click "Try it out"
5. Upload an image file
6. Click "Execute"
7. Download the processed image from the response

## Example Use Cases

### Portrait/Headshot Processing
```python
# Use human segmentation model for best results with people
params = {
    "model": "u2net_human_seg",
    "alpha_matting": True
}
```

### Product Photography
```python
# Use default model with custom background
params = {
    "model": "u2net",
    "background_color": "255,255,255"  # White background
}
```

### Sharp-Edged Graphics
```python
# Use smaller erosion size for sharper edges
params = {
    "model": "u2net",
    "alpha_matting": True,
    "alpha_matting_erode_size": 3
}
```

## Troubleshooting

### Slow Processing
- Install PyTorch with CUDA support for GPU acceleration
- Use `u2netp` model for faster (but slightly lower quality) results
- Check GPU availability: `python -c "import torch; print(torch.cuda.is_available())"`

### Out of Memory Errors
- Process smaller images
- Use `u2netp` model (smaller memory footprint)

### Background Not Fully Removed
- Try `u2net_human_seg` model for people/portraits
- Enable `alpha_matting=true` for better edge detection
- Adjust `alpha_matting_foreground_threshold` and `alpha_matting_background_threshold`

## Credits

This API is powered by:
- [backgroundremover](https://github.com/nadermx/backgroundremover) - Background removal library
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [U-2-Net](https://github.com/xuebinqin/U-2-Net) - Deep learning architecture

## License

MIT License - Feel free to use in your projects!
