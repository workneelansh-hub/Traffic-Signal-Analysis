# Quick Start Guide - Approach 2

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
cd "Approach 2"
pip install -r requirements.txt
```

### 2. Test on Image
```bash
python examples/Example.py
```

### 3. Process Video
```bash
python process_video.py --input ../trafficv2.mp4 --model nano
```

## 📋 Command Line Options

### Basic Usage
```bash
python process_video.py --input <video_path> --model <nano|small|medium>
```

### Full Options
```bash
python process_video.py \
    --input ../trafficv2.mp4 \
    --model nano \
    --output output.mp4 \
    --conf 0.25 \
    --preview
```

### Arguments:
- `--input, -i`: Input video file path
- `--model, -m`: Model size (nano, small, medium)
- `--output, -o`: Output video file path
- `--conf, -c`: Confidence threshold (0-1)
- `--preview, -p`: Show live preview window

## 🎯 Example Commands

### Fast Processing (Nano Model)
```bash
python process_video.py -i ../trafficv2.mp4 -m nano -o output_nano.mp4
```

### Best Accuracy (Medium Model)
```bash
python process_video.py -i ../trafficv2.mp4 -m medium -o output_medium.mp4
```

### With Live Preview
```bash
python process_video.py -i ../trafficv2.mp4 -m small -p
```

## ⚡ Performance Comparison

| Model | Speed (CPU) | Accuracy | Use Case |
|-------|------------|----------|----------|
| Nano | ~44ms/frame | Good | Real-time, fast |
| Small | ~72ms/frame | Better | Balanced |
| Medium | ~130ms/frame | Best | High accuracy |

## 📊 Output

The script generates:
- Processed video with detections
- Performance metrics (FPS, inference time)
- Detection statistics (count, classes)

## ❓ Troubleshooting

**Import Error?**
```bash
pip install --upgrade ultralytics
```

**Video not found?**
- Check file path (use relative path from Approach 2 folder)
- Example: `../trafficv2.mp4` (one folder up)

**Slow processing?**
- Use nano model: `--model nano`
- Lower confidence: `--conf 0.3`
- Use GPU if available (automatic)

