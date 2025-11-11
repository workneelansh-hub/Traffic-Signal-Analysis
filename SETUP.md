# Setup Guide - Approach 2: Traffic Light Detection

This guide will help you set up and run the Traffic Light Detection system using YOLOv8 models.

## 📋 Requirements

### Hardware Requirements

**Minimum:**
- **CPU**: Multi-core processor (Intel Core i5 or AMD equivalent)
- **RAM**: 2 GB (4 GB recommended)
- **Storage**: 500 MB free space
- **GPU**: Optional (CPU works fine, GPU recommended for better performance)

**Recommended:**
- **CPU**: Intel Core i7/AMD Ryzen 7 or Apple M1/M2
- **RAM**: 4-8 GB
- **GPU**: NVIDIA GTX 1660+ or Apple Silicon GPU (optional but recommended)
- **Storage**: 2-5 GB free space

### Software Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows 10/11, macOS, or Linux
- **pip**: Latest version

## 🚀 Installation Steps

### Step 1: Navigate to Approach 2 Directory

```bash
cd "Approach 2"
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
python -c "from ultralytics import YOLO; print('Installation successful!')"
```

## 📝 Available Models

The repository includes three pre-trained YOLOv8 models:

1. **Nano Model** (`best_traffic_nano_yolo.pt`)
   - Size: ~6 MB
   - Speed: ~43.7 ms per frame (Mac M1 Max CPU)
   - Best for: Real-time applications, resource-constrained devices

2. **Small Model** (`best_traffic_small_yolo.pt`)
   - Size: ~22 MB
   - Speed: ~72.1 ms per frame (Mac M1 Max CPU)
   - Best for: Balanced performance and accuracy

3. **Medium Model** (`best_traffic_med_yolo_v8.pt`)
   - Size: ~52 MB
   - Speed: ~130.2 ms per frame (Mac M1 Max CPU)
   - Best for: Higher accuracy requirements

## 🎯 Usage Examples

### Example 1: Test on Single Image

```bash
python examples/Example.py
```

### Example 2: Live Webcam Test

```bash
python "examples/Webcam Example.py"
```

### Example 3: Process Video File

```bash
python process_video.py --input ../trafficv2.mp4 --model nano --output output_approach2.mp4
```

## 🔧 Troubleshooting

### Issue: Import Error for ultralytics
**Solution:**
```bash
pip install --upgrade ultralytics
```

### Issue: CUDA/GPU not detected
**Solution:**
- Check if you have NVIDIA GPU: `nvidia-smi`
- Install CUDA-compatible PyTorch:
  ```bash
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
  ```

### Issue: OpenCV not working
**Solution:**
```bash
pip uninstall opencv-python opencv-python-headless
pip install opencv-python
```

### Issue: Out of Memory
**Solution:**
- Use the nano model instead of medium
- Reduce video resolution
- Process fewer frames per second

## 📊 Performance Tips

1. **For Real-time Processing**: Use nano or small model
2. **For Best Accuracy**: Use medium model
3. **GPU Acceleration**: Automatically used if available (CUDA/Apple Silicon)
4. **CPU Only**: Works fine but slower (especially for medium model)

## 📚 Additional Resources

- [Ultralytics YOLOv8 Documentation](https://docs.ultralytics.com/)
- [Repository README](README.md)

