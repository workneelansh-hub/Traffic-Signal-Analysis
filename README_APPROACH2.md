# Approach 2 - Complete Setup and Usage Guide

## 📁 What's Included

This folder contains a complete setup for running YOLOv8-based traffic light detection with video processing capabilities.

### Files Created:

1. **`requirements.txt`** - All Python dependencies needed
2. **`process_video.py`** - Main video processing script with timing metrics
3. **`SETUP.md`** - Detailed setup instructions
4. **`RUN_STEPS.md`** - Step-by-step execution guide
5. **`QUICK_START.md`** - Quick reference for common tasks

### Original Repository Files:

- `models/` - Three pre-trained YOLOv8 models (nano, small, medium)
- `examples/` - Original example scripts
- `README.md` - Original repository documentation

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies
```bash
cd "Approach 2"
pip install -r requirements.txt
```

### 2. Test Installation
```bash
python examples/Example.py
```

### 3. Process Video
```bash
python process_video.py --input ../trafficv2.mp4 --model nano
```

## 📊 Video Processing Script Features

The `process_video.py` script provides:

✅ **Video Processing**: Process any video file with traffic light detection  
✅ **Performance Metrics**: Real-time FPS, inference time, processing speed  
✅ **Detection Statistics**: Count of detections, class breakdown  
✅ **Multiple Models**: Choose between nano, small, or medium models  
✅ **Live Preview**: Optional preview window during processing  
✅ **Configurable**: Adjustable confidence threshold  

## 🎯 Usage Examples

### Basic Usage
```bash
python process_video.py -i ../trafficv2.mp4 -m nano
```

### With All Options
```bash
python process_video.py \
    --input ../trafficv2.mp4 \
    --model small \
    --output my_output.mp4 \
    --conf 0.3 \
    --preview
```

### Model Comparison
```bash
# Fast processing
python process_video.py -i ../trafficv2.mp4 -m nano -o output_nano.mp4

# Balanced
python process_video.py -i ../trafficv2.mp4 -m small -o output_small.mp4

# Best accuracy
python process_video.py -i ../trafficv2.mp4 -m medium -o output_medium.mp4
```

## 📈 Expected Performance

Based on repository benchmarks (Mac M1 Max CPU):

| Model | Inference Time | FPS (approx) | Use Case |
|-------|---------------|--------------|----------|
| Nano | ~44ms | ~23 FPS | Real-time, fast |
| Small | ~72ms | ~14 FPS | Balanced |
| Medium | ~130ms | ~8 FPS | High accuracy |

**Note**: Performance will vary based on hardware. GPU acceleration is automatic if available.

## 📋 Requirements Summary

### Minimum Hardware:
- **CPU**: Multi-core (Intel i5 or equivalent)
- **RAM**: 2 GB (4 GB recommended)
- **Storage**: 500 MB free
- **GPU**: Optional (CPU works fine)

### Software:
- **Python**: 3.8+
- **OS**: Windows, macOS, or Linux
- **Dependencies**: See `requirements.txt`

## 📚 Documentation Files

- **`SETUP.md`** - Complete setup guide with troubleshooting
- **`RUN_STEPS.md`** - Detailed step-by-step instructions
- **`QUICK_START.md`** - Quick reference guide
- **`README.md`** - Original repository documentation

## 🔍 What the Script Does

1. **Loads Model**: Loads selected YOLOv8 model (nano/small/medium)
2. **Opens Video**: Reads input video file
3. **Processes Frames**: Runs detection on each frame
4. **Tracks Metrics**: Records inference time, FPS, detections
5. **Saves Output**: Writes annotated video with detections
6. **Displays Stats**: Shows comprehensive performance metrics

## 📊 Output Information

After processing, you'll see:

- Total processing time
- Average FPS
- Inference time statistics (min/max/avg)
- Total detections
- Detection breakdown by class
- Processing speed vs real-time

## 🎓 Next Steps

1. ✅ Run the setup steps from `RUN_STEPS.md`
2. ✅ Test with example scripts
3. ✅ Process your video files
4. ✅ Compare different models
5. ✅ Analyze performance metrics

## 💡 Tips

- Start with **nano** model for fastest processing
- Use **medium** model for best accuracy
- Add `--preview` to watch processing live
- Lower `--conf` value for more detections
- GPU automatically used if available

## 🆘 Need Help?

1. Check `SETUP.md` for detailed setup
2. Review `RUN_STEPS.md` for step-by-step guide
3. See `QUICK_START.md` for quick reference
4. Check error messages for specific issues

---

**Ready to start?** Follow the steps in `RUN_STEPS.md`!

