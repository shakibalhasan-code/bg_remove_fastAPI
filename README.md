# Background Remover API

A production-ready FastAPI application for removing backgrounds from images using AI. Powered by the popular [backgroundremover](https://github.com/nadermx/backgroundremover) library.

🔗 **Repository**: https://github.com/shakibalhasan-code/bg_remove_fastAPI

## ✨ Features

- 🎨 AI-powered background removal
- 🚀 Fast REST API built with FastAPI
- 🎯 Multiple AI models (u2net, u2net_human_seg, u2netp)
- 🔧 Customizable options (custom backgrounds, masks, edge quality)
- 💾 Memory-efficient (no disk storage, direct streaming)
- 📝 Interactive API documentation (Swagger UI)
- 🖼️ Supports JPG, PNG, HEIC, HEIF formats
- 🔒 Production-ready with CORS, logging, and error handling

## 🚀 Quick Deploy to Hostinger VPS

### One-Command Deployment:

```bash
# SSH into your VPS
ssh root@YOUR_VPS_IP

# Download and run deployment script
wget https://raw.githubusercontent.com/shakibalhasan-code/bg_remove_fastAPI/master/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

**Done!** Your API is now running. See [HOSTINGER_DEPLOYMENT.md](HOSTINGER_DEPLOYMENT.md) for details.

## 📖 Documentation

- **[HOSTINGER_DEPLOYMENT.md](HOSTINGER_DEPLOYMENT.md)** - Complete VPS deployment guide
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute deployment checklist
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Advanced deployment options (Docker, systemd)

## 🔄 Update Workflow

After pushing changes to GitHub:

```bash
# SSH to VPS
ssh root@YOUR_VPS_IP

# Run update script
cd /var/www/bg_remove
./update.sh
```

## 🧪 Local Development

```bash
# Clone repository
git clone https://github.com/shakibalhasan-code/bg_remove_fastAPI.git
cd bg_remove_fastAPI

# Install dependencies
pip install -r requirements.txt

# Run development server
python main.py
```

Visit http://localhost:8000/docs

## 📡 API Endpoints

### Simple Background Removal
```bash
POST /remove-background-simple
```
Upload an image and get transparent PNG back.

### Advanced Background Removal
```bash
POST /remove-background
```
Full control with parameters:
- `model`: AI model choice (u2net, u2net_human_seg, u2netp)
- `background_color`: Custom background (e.g., "255,0,0" for red)
- `only_mask`: Return binary mask instead

### Health Check
```bash
GET /health
```

## 💻 Usage Examples

### cURL
```bash
curl -X POST "http://YOUR_VPS_IP/remove-background-simple" \
  -F "file=@image.jpg" \
  -o output.png
```

### Python
```python
import requests

with open("input.jpg", "rb") as f:
    response = requests.post(
        "http://YOUR_VPS_IP/remove-background-simple",
        files={"file": f}
    )

with open("output.png", "wb") as f:
    f.write(response.content)
```

### JavaScript (Fetch)
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://YOUR_VPS_IP/remove-background-simple', {
    method: 'POST',
    body: formData
})
.then(response => response.blob())
.then(blob => {
    const url = URL.createObjectURL(blob);
    // Use the image
});
```

## 🔧 Configuration

### Update CORS Origins
Edit `main.py`:
```python
ALLOWED_ORIGINS = ["https://your-frontend-domain.com"]
```

### Adjust File Size Limit
Edit `main.py`:
```python
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
```

### Configure Workers (Performance)
Edit `gunicorn_conf.py`:
```python
workers = (2 * CPU_CORES) + 1
```

## 🛠️ Useful Commands

```bash
# Check API status
sudo systemctl status bg-remover-api

# View logs
sudo journalctl -u bg-remover-api -f

# Restart API
sudo systemctl restart bg-remover-api

# Test health
curl http://localhost:8000/health
```

## 📊 System Requirements

- **RAM**: 2GB minimum, 4GB+ recommended
- **Python**: 3.10 or 3.11 (3.13 has compatibility issues)
- **Disk**: ~500MB for models and dependencies
- **OS**: Ubuntu 20.04+

## 🔒 Security Features

- CORS middleware (configurable)
- File size validation (10MB default)
- File type validation
- Request logging
- Error handling
- Health check endpoint

## 🎯 Performance Tips

1. **Use GPU** for 5-10x faster processing
2. **Adjust workers** based on CPU cores
3. **Enable caching** - models cached after first use
4. **Use CDN** for high traffic
5. **Choose right model**:
   - `u2net`: Best quality (default)
   - `u2net_human_seg`: Best for portraits
   - `u2netp`: Fastest processing

## 📝 License

MIT License - Feel free to use in your projects!

## 🙏 Credits

- [backgroundremover](https://github.com/nadermx/backgroundremover) - Background removal library
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [U-2-Net](https://github.com/xuebinqin/U-2-Net) - Deep learning model

## 📞 Support

- Issues: [GitHub Issues](https://github.com/shakibalhasan-code/bg_remove_fastAPI/issues)
- Documentation: See [HOSTINGER_DEPLOYMENT.md](HOSTINGER_DEPLOYMENT.md)

---

Made with ❤️ for production deployment


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
