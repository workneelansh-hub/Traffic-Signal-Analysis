# Process Video Realtime V2 - Front-Only Detection Guide

## Overview

`process_video_realtime_v2.py` is a modified version that **only detects traffic lights in front of the dashcam**, filtering out side lights. This is ideal for dashcam applications where you only care about lights directly ahead.

## Key Features

✅ **Front-Only Detection**: Filters out side traffic lights  
✅ **Configurable Region**: Adjustable front detection area  
✅ **Preview Mode Default**: Optimized for live viewing (no save by default)  
✅ **Visual Guide**: Shows front detection region on screen  
✅ **Same Performance**: All other features from v1 (alerts, frame skipping, etc.)  

## Quick Start

### Basic Usage (Preview Only)
```bash
python process_video_realtime_v2.py -i ../trafficv2.mp4
```

### With Custom Model
```bash
python process_video_realtime_v2.py -i ../trafficv2.mp4 -m small
```

### Save Output Video
```bash
python process_video_realtime_v2.py -i ../trafficv2.mp4 --save
```

## Front Detection Filter

The script filters detections based on:

1. **Horizontal Position**: Only center portion (default: center 40%)
   - Excludes left and right edges where side lights appear
   - Configurable with `--center-margin` (default: 0.3 = 30% margin from each side)

2. **Vertical Position**: Only top portion (default: top 60%)
   - Traffic lights are typically in upper portion of frame
   - Configurable with `--top-portion` (default: 0.6 = top 60%)

### Visual Guide

When preview is enabled, you'll see:
- **Green rectangle**: Front detection region boundary
- **Detections**: Only traffic lights within the green region are shown and tracked

## Command Line Options

```
--input, -i          Input video file path
--model, -m          Model size (nano, small, medium) [default: nano]
--output, -o         Output video file path [default: output_realtime_v2.mp4]
--conf, -c           Confidence threshold (0-1) [default: 0.25]
--target-fps, -f     Target processing FPS [default: 10]
--no-preview         Disable live preview window
--save               Save output video (default: preview only, no save)
--center-margin      Margin from edges (0.3 = center 40%) [default: 0.3]
--top-portion        Top portion to consider (0.6 = top 60%) [default: 0.6]
```

## Examples

### Adjust Front Detection Region

**Wider front region (center 60%):**
```bash
python process_video_realtime_v2.py -i ../trafficv2.mp4 --center-margin 0.2
```

**Narrower front region (center 30%):**
```bash
python process_video_realtime_v2.py -i ../trafficv2.mp4 --center-margin 0.35
```

**Consider more of frame vertically (top 80%):**
```bash
python process_video_realtime_v2.py -i ../trafficv2.mp4 --top-portion 0.8
```

**Consider less of frame vertically (top 50%):**
```bash
python process_video_realtime_v2.py -i ../trafficv2.mp4 --top-portion 0.5
```

### Full Example with Custom Settings
```bash
python process_video_realtime_v2.py \
    -i ../trafficv2.mp4 \
    -m nano \
    --center-margin 0.25 \
    --top-portion 0.65 \
    --save \
    -o my_output.mp4
```

## How It Works

1. **Detection**: YOLO detects all traffic lights in frame
2. **Filtering**: Only keeps detections where:
   - Bounding box center X is within center region (30%-70% by default)
   - Bounding box center Y is in top portion (0%-60% by default)
3. **Tracking**: Only filtered (front) detections are tracked
4. **Alerts**: Only color changes from front lights trigger alerts

## Comparison: V1 vs V2

| Feature | V1 | V2 |
|---------|----|----|
| All detections | ✅ | ❌ |
| Front-only | ❌ | ✅ |
| Side lights filtered | ❌ | ✅ |
| Visual region guide | ❌ | ✅ |
| Default save | ✅ | ❌ (preview mode) |
| Configurable region | ❌ | ✅ |

## Tips

1. **For narrow roads**: Use smaller `--center-margin` (e.g., 0.35)
2. **For wide roads**: Use larger `--center-margin` (e.g., 0.25)
3. **For elevated lights**: Increase `--top-portion` (e.g., 0.7)
4. **For low lights**: Decrease `--top-portion` (e.g., 0.5)
5. **Adjust in real-time**: Watch the green rectangle to see the detection region

## Troubleshooting

### Too Many Side Lights Detected
- Decrease `--center-margin` (e.g., 0.35)
- Decrease `--top-portion` (e.g., 0.5)

### Missing Front Lights
- Increase `--center-margin` (e.g., 0.25)
- Increase `--top-portion` (e.g., 0.7)

### Green Rectangle Not Visible
- Ensure preview is enabled (don't use `--no-preview`)
- Rectangle is semi-transparent, look for green border

## Statistics

The script shows:
- **Front Detections**: Count of detections after filtering
- **Alerts**: Only from front-facing traffic lights
- **Detection stats**: Only includes front detections

---

**Perfect for**: Dashcam applications, front-facing detection, reducing false alerts from side lights

