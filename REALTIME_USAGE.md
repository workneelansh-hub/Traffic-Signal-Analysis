# Real-Time Video Processing Guide

## Overview

The `process_video_realtime.py` script processes videos at approximately 10 FPS with:
- ✅ **Frame Skipping**: Automatically skips frames based on video FPS (30 FPS = skip 3, 60 FPS = skip 6)
- ✅ **Live Preview**: Real-time visualization of detections
- ✅ **Color Change Alerts**: Alerts when traffic light changes color (Red/Yellow/Green)
- ✅ **Performance Metrics**: Real-time FPS and inference time display

## Quick Start

### Basic Usage
```bash
python process_video_realtime.py --input ../trafficv2.mp4
```

### With Custom Model
```bash
python process_video_realtime.py -i ../trafficv2.mp4 -m small
```

### Preview Only (No Save)
```bash
python process_video_realtime.py -i ../trafficv2.mp4 --no-save
```

## Command Line Options

```
--input, -i          Input video file path
--model, -m          Model size (nano, small, medium) [default: nano]
--output, -o         Output video file path [default: output_realtime.mp4]
--conf, -c           Confidence threshold (0-1) [default: 0.25]
--target-fps, -f     Target processing FPS [default: 10]
--no-preview         Disable live preview window
--no-save            Do not save output video (preview only)
```

## Frame Skipping Logic

The script automatically calculates frame skipping based on video FPS:

- **30 FPS video**: Skips 3 frames, processes every 4th frame (~7.5 FPS)
- **60 FPS video**: Skips 6 frames, processes every 7th frame (~8.57 FPS)
- **Other FPS**: Auto-calculated to achieve ~10 FPS

This ensures real-time processing speed while maintaining detection quality.

## Alert System

The script includes an intelligent alert system that:

1. **Tracks Traffic Lights**: Uses YOLO tracking to follow individual traffic lights across frames
2. **Detects Color Changes**: Monitors when a traffic light changes from:
   - Red → Yellow
   - Red → Green
   - Yellow → Red
   - Yellow → Green
   - Green → Red
   - Green → Yellow
3. **Alert Cooldown**: Prevents spam with 1-second cooldown between alerts per traffic light
4. **Console Output**: Prints alerts to console in real-time
5. **Visual Indicator**: Shows alert on preview window

### Alert Example
```
🚨 ALERT: Traffic light changed from RED to GREEN
🚨 ALERT: Traffic light changed from GREEN to YELLOW
```

## Live Preview Features

The preview window shows:
- **Video Feed**: Real-time processed frames with detections
- **Info Overlay**: 
  - Current frame number
  - Processed frames count
  - Processing FPS
  - Inference time
  - Total detections
  - Alert count
- **Alert Indicator**: Red text showing recent color changes

## Controls

- **'q'**: Quit processing
- **'p'**: Pause/Resume processing

## Performance Tips

1. **For Best Speed**: Use `nano` model (`-m nano`)
2. **For Best Accuracy**: Use `medium` model (`-m medium`)
3. **Lower Confidence**: Use `--conf 0.3` for more detections
4. **Preview Only**: Use `--no-save` to skip video encoding (faster)

## Example Commands

### Real-time Processing with Alerts
```bash
python process_video_realtime.py -i ../trafficv2.mp4 -m nano
```

### High Accuracy with Alerts
```bash
python process_video_realtime.py -i ../trafficv2.mp4 -m medium
```

### Preview Only (No Save)
```bash
python process_video_realtime.py -i ../trafficv2.mp4 --no-save
```

### Custom Target FPS
```bash
python process_video_realtime.py -i ../trafficv2.mp4 --target-fps 15
```

## Output Information

After processing, you'll see:
- Total processing time
- Processed frames count
- Average processing FPS
- Inference time statistics
- Detection statistics by class
- Alert summary with recent color changes

## Troubleshooting

### Alerts Not Showing
- Ensure traffic lights are being detected (check detection count)
- Color changes require tracking - ensure objects are tracked across frames
- Check console output for alert messages

### Preview Window Not Showing
- Remove `--no-preview` flag
- Ensure you have display/GUI access
- On remote servers, preview may not work

### Processing Too Slow
- Use `nano` model
- Lower confidence threshold
- Reduce target FPS

### Too Many Alerts
- Increase alert cooldown in code (default: 1.0 seconds)
- Check if detections are flickering (may need confidence adjustment)

## Technical Details

- **Tracking**: Uses ByteTrack algorithm for object tracking
- **Frame Rate Control**: Sleeps between frames to maintain target FPS
- **Memory Management**: Cleans up old tracking IDs automatically
- **Alert Cooldown**: 1 second minimum between alerts per traffic light

