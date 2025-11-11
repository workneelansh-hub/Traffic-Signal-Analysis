"""
Real-Time Video Processing Script for Approach 2 - Traffic Light Detection (V2)
Processes video at 10 FPS with frame skipping, live preview, and color change alerts.
V2: Filters to only detect traffic lights in front of dashcam (ignores side lights).
"""

import cv2
import argparse
import time
from pathlib import Path
from ultralytics import YOLO
from collections import defaultdict, deque
import numpy as np
from datetime import datetime


class TrafficLightAlertSystem:
    """Alert system for traffic light color changes"""
    
    def __init__(self, alert_cooldown=1.0):
        """
        Initialize alert system.
        
        Args:
            alert_cooldown: Minimum seconds between alerts (default: 1.0)
        """
        self.alert_cooldown = alert_cooldown
        self.last_alert_time = {}
        self.last_detected_colors = {}  # Track last color per detection ID
        self.alert_sound_enabled = False  # Can be extended with sound alerts
        
    def check_color_change(self, detections, current_time):
        """
        Check for color changes and generate alerts.
        
        Args:
            detections: List of detection results with boxes (from YOLO track)
            current_time: Current timestamp
            
        Returns:
            List of alert messages
        """
        alerts = []
        
        if not detections:
            return alerts
        
        for detection in detections:
            boxes = detection.boxes
            if boxes is None or len(boxes) == 0:
                continue
            
            # Process each tracked detection
            for box in boxes:
                # Get tracking ID if available
                if box.id is not None and len(box.id) > 0:
                    detection_id = int(box.id[0])
                else:
                    # Fallback: use bbox center as ID for untracked detections
                    bbox = box.xyxy[0].cpu().numpy()
                    detection_id = f"bbox_{int(bbox[0])}_{int(bbox[1])}"
                
                # Get detected color
                cls = int(box.cls[0])
                color = detection.names[cls].lower()
                
                # Check if color changed
                if detection_id in self.last_detected_colors:
                    last_color = self.last_detected_colors[detection_id]
                    if last_color != color:
                        # Color changed - check cooldown
                        if detection_id not in self.last_alert_time or \
                           (current_time - self.last_alert_time[detection_id]) >= self.alert_cooldown:
                            alerts.append({
                                'id': detection_id,
                                'from': last_color,
                                'to': color,
                                'time': current_time,
                                'confidence': float(box.conf[0])
                            })
                            self.last_alert_time[detection_id] = current_time
                
                # Update last detected color
                self.last_detected_colors[detection_id] = color
        
        # Clean up old tracking IDs (not detected in current frame)
        current_ids = set()
        for detection in detections:
            boxes = detection.boxes
            if boxes is not None:
                for box in boxes:
                    if box.id is not None and len(box.id) > 0:
                        current_ids.add(int(box.id[0]))
        
        # Remove old IDs (keep for a few frames in case of temporary occlusion)
        ids_to_remove = []
        for det_id in self.last_detected_colors.keys():
            if isinstance(det_id, int) and det_id not in current_ids:
                # Mark for removal but keep for a few more frames
                if det_id not in getattr(self, '_pending_removal', {}):
                    self._pending_removal = getattr(self, '_pending_removal', {})
                    self._pending_removal[det_id] = current_time
                elif current_time - self._pending_removal[det_id] > 2.0:  # Remove after 2 seconds
                    ids_to_remove.append(det_id)
        
        for det_id in ids_to_remove:
            if det_id in self.last_detected_colors:
                del self.last_detected_colors[det_id]
            if det_id in self.last_alert_time:
                del self.last_alert_time[det_id]
        
        return alerts


def filter_front_detections_simple(results, frame_width, frame_height,
                                   center_margin=0.3, top_portion=0.6):
    """
    Simplified filter that modifies results in-place by removing side detections.
    This version works directly with YOLO results structure.
    
    Args:
        results: YOLO detection results (will be modified)
        frame_width: Frame width
        frame_height: Frame height
        center_margin: Margin from edges (0.3 = 30% from each side)
        top_portion: Top portion to consider (0.6 = top 60%)
    """
    import torch
    
    # Calculate front region boundaries
    left_boundary = frame_width * center_margin
    right_boundary = frame_width * (1 - center_margin)
    bottom_boundary = frame_height * top_portion
    
    for result in results:
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            continue
        
        # Get all box data
        box_xyxy = boxes.xyxy.cpu().numpy()
        keep_indices = []
        
        for i, bbox in enumerate(box_xyxy):
            x1, y1, x2, y2 = bbox
            
            # Calculate center
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            # Check if in front region
            is_centered = left_boundary <= center_x <= right_boundary
            is_in_upper = center_y <= bottom_boundary
            
            if is_centered and is_in_upper:
                keep_indices.append(i)
        
        # Filter boxes to keep only front detections
        if len(keep_indices) < len(box_xyxy):
            keep_mask = torch.zeros(len(box_xyxy), dtype=torch.bool, device=boxes.xyxy.device)
            if len(keep_indices) > 0:
                keep_tensor = torch.tensor(keep_indices, dtype=torch.long, device=boxes.xyxy.device)
                keep_mask[keep_tensor] = True

            result.boxes = boxes[keep_mask]


def calculate_display_size(frame_width, frame_height, max_width=1280, max_height=720):
    """
    Calculate display size that fits on screen while maintaining aspect ratio.
    
    Args:
        frame_width: Original frame width
        frame_height: Original frame height
        max_width: Maximum display width (default: 1920)
        max_height: Maximum display height (default: 1080)
        
    Returns:
        Tuple of (display_width, display_height)
    """
    # Calculate scale factors for both dimensions
    scale_w = max_width / frame_width
    scale_h = max_height / frame_height
    
    # Use the smaller scale to ensure both dimensions fit
    scale = min(scale_w, scale_h, 1.0)  # Don't upscale if already smaller
    
    display_width = int(frame_width * scale)
    display_height = int(frame_height * scale)
    
    return display_width, display_height


def calculate_frame_skip(video_fps, target_fps=10):
    """
    Calculate how many frames to skip to achieve target FPS.
    
    Args:
        video_fps: Original video FPS
        target_fps: Desired processing FPS (default: 10)
        
    Returns:
        Number of frames to skip
    """
    if video_fps <= target_fps:
        return 0  # Process all frames if video FPS is already <= target
    
    # User specified frame skipping:
    # 30 FPS: skip 3 frames (process every 4th frame = 30/4 = 7.5 FPS)
    # 60 FPS: skip 6 frames (process every 7th frame = 60/7 ≈ 8.57 FPS)
    # This gives approximately 10 FPS processing rate
    
    if abs(video_fps - 30) < 1:  # Handle 30 FPS (with small tolerance)
        return 3  # Skip 3 frames, process every 4th
    elif abs(video_fps - 60) < 1:  # Handle 60 FPS (with small tolerance)
        return 6  # Skip 6 frames, process every 7th
    else:
        # Auto-calculate for other FPS values to achieve ~10 FPS
        # To get target_fps from video_fps: process every (video_fps/target_fps) frames
        # So skip (video_fps/target_fps - 1) frames
        skip_count = int(video_fps / target_fps) - 1
        return max(0, skip_count)


def process_video_realtime(
    video_path,
    model_path='models/best_traffic_nano_yolo.pt',
    output_path='output_realtime.mp4',
    conf_threshold=0.25,
    target_fps=10,
    show_preview=True,
    save_output=False,  # Default to False for v2 (preview mode)
    center_margin=0.3,  # 30% margin from edges (center 40% is front)
    top_portion=0.6     # Top 60% of frame
):
    """
    Process video file in real-time with frame skipping, live preview, and alerts.
    V2: Only detects traffic lights in front of dashcam (filters side lights).
    
    Args:
        video_path: Path to input video file
        model_path: Path to YOLOv8 model (.pt file)
        output_path: Path to save output video
        conf_threshold: Confidence threshold for detections (0-1)
        target_fps: Target processing FPS (default: 10)
        show_preview: Whether to show live preview window
        save_output: Whether to save output video (default: False for preview mode)
        center_margin: Margin from edges for front detection (0.3 = center 40%)
        top_portion: Top portion of frame to consider (0.6 = top 60%)
    """
    
    print("=" * 70)
    print("Approach 2 V2: Real-Time Traffic Light Detection (Front-Only)")
    print("=" * 70)
    
    # Load model
    print(f"\n📦 Loading model: {model_path}")
    try:
        model = YOLO(model_path)
        print(f"✅ Model loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return
    
    # Open video
    print(f"\n📹 Opening video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error: Could not open video {video_path}")
        return
    
    # Get video properties
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Calculate display size for preview (fits on screen)
    display_width, display_height = calculate_display_size(width, height)
    
    # Calculate frame skip
    frames_to_skip = calculate_frame_skip(video_fps, target_fps)
    actual_processing_fps = video_fps / (frames_to_skip + 1) if frames_to_skip > 0 else video_fps
    
    # Calculate front detection region
    left_boundary = int(width * center_margin)
    right_boundary = int(width * (1 - center_margin))
    bottom_boundary = int(height * top_portion)
    
    print(f"\n📊 Video Information:")
    print(f"   Resolution: {width}x{height}")
    print(f"   Video FPS: {video_fps:.1f}")
    print(f"   Total Frames: {total_frames}")
    print(f"   Duration: {total_frames/video_fps:.1f}s")
    print(f"\n⚙️  Processing Configuration:")
    print(f"   Target FPS: {target_fps}")
    print(f"   Frames to Skip: {frames_to_skip}")
    print(f"   Actual Processing FPS: {actual_processing_fps:.1f}")
    print(f"\n🎯 Front Detection Filter:")
    print(f"   Horizontal: Center {int((1-2*center_margin)*100)}% ({left_boundary}-{right_boundary}px)")
    print(f"   Vertical: Top {int(top_portion*100)}% (0-{bottom_boundary}px)")
    if show_preview:
        print(f"   Display Size: {display_width}x{display_height} (fits on screen)")
    
    # Video writer (if saving output)
    out = None
    if save_output:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, target_fps, (width, height))
        print(f"   Output will be saved to: {output_path}")
    else:
        print(f"   Preview mode: No output file will be saved")
    
    # Initialize alert system
    alert_system = TrafficLightAlertSystem(alert_cooldown=1.0)
    
    # Statistics
    frame_count = 0
    processed_frames = 0
    total_detections = 0
    filtered_detections = 0  # Count of detections after filtering
    inference_times = deque(maxlen=30)
    detection_stats = defaultdict(int)
    alert_history = []
    last_processed_frame = None  # Store last processed frame for display
    
    start_time = time.time()
    last_frame_time = start_time
    frame_interval = 1.0 / target_fps  # Time between processed frames
    
    print(f"\n🚀 Starting real-time processing...")
    print(f"   Press 'q' to quit, 'p' to pause\n")
    
    paused = False
    alerts = []  # Initialize alerts list
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            current_time = time.time()
            
            # Handle pause
            if paused:
                if show_preview and last_processed_frame is not None:
                    # Resize for display during pause
                    display_frame = cv2.resize(last_processed_frame, (display_width, display_height), interpolation=cv2.INTER_LINEAR)
                    cv2.imshow('Real-Time Traffic Light Detection - Approach 2 V2', display_frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('p'):
                    paused = False
                    print("▶️  Resumed")
                elif key == ord('q'):
                    break
                continue
            
            # Frame skipping logic
            should_process = False
            if frames_to_skip == 0:
                should_process = True
            else:
                # Process every (frames_to_skip + 1)th frame
                # For 30 FPS with skip 3: process frames 1, 5, 9, 13... (every 4th frame)
                if frame_count % (frames_to_skip + 1) == 1:
                    should_process = True
            
            if should_process:
                processed_frames += 1
                
                # Control processing speed to match target FPS
                elapsed_since_last = current_time - last_frame_time
                if elapsed_since_last < frame_interval:
                    time.sleep(frame_interval - elapsed_since_last)
                
                # Run inference with tracking for better color change detection
                inference_start = time.time()
                results = model.track(
                    frame,
                    conf=conf_threshold,
                    verbose=False,
                    imgsz=640,
                    persist=True,
                    tracker='bytetrack.yaml'  # Use ByteTrack for object tracking
                )
                inference_time = (time.time() - inference_start) * 1000  # Convert to ms
                inference_times.append(inference_time)
                
                # Count total detections before filtering
                total_before_filter = 0
                for result in results:
                    if result.boxes is not None:
                        total_before_filter += len(result.boxes)
                
                # Filter to only front-facing detections
                filter_front_detections_simple(results, width, height, center_margin, top_portion)
                
                # Count detections after filtering
                total_after_filter = 0
                for result in results:
                    if result.boxes is not None:
                        total_after_filter += len(result.boxes)
                
                filtered_detections += total_after_filter
                
                # Check for color changes and generate alerts (only on front detections)
                alerts = alert_system.check_color_change(results, current_time)
                if alerts:
                    for alert in alerts:
                        alert_msg = f"🚨 ALERT: Traffic light changed from {alert['from'].upper()} to {alert['to'].upper()}"
                        print(f"\n{alert_msg}")
                        alert_history.append(alert)
                
                # Process results
                annotated_frame = frame.copy()
                
                # Draw front detection region (optional visual guide)
                if show_preview:
                    # Draw semi-transparent rectangle for front region
                    overlay_region = frame.copy()
                    cv2.rectangle(overlay_region, 
                                (left_boundary, 0), 
                                (right_boundary, bottom_boundary), 
                                (0, 255, 0), 2)  # Green border
                    cv2.addWeighted(overlay_region, 0.1, frame, 0.9, 0, annotated_frame)
                
                for result in results:
                    # Draw detections on frame
                    annotated_frame = result.plot()
                    
                    # Count detections
                    boxes = result.boxes
                    if boxes is not None:
                        num_detections = len(boxes)
                        total_detections += num_detections
                        
                        # Count by class
                        for box in boxes:
                            cls = int(box.cls[0])
                            cls_name = result.names[cls]
                            detection_stats[cls_name] += 1
                
                frame = annotated_frame
                last_processed_frame = frame.copy()  # Store for skipped frames
                last_frame_time = time.time()
            else:
                # For skipped frames, use the current frame (no annotations)
                # or reuse last processed frame if available
                if last_processed_frame is not None:
                    # Option: Use last processed frame (shows detections on skipped frames)
                    frame = last_processed_frame.copy()
                # Option: Use current frame without annotations (more accurate but no detections)
                # frame = frame  # (already set from cap.read())
            
            # Add info overlay
            elapsed_total = time.time() - start_time
            current_fps = processed_frames / elapsed_total if elapsed_total > 0 else 0
            avg_inference = np.mean(inference_times) if inference_times else 0
            
            # Create overlay with same dimensions as frame
            overlay = frame.copy()
            overlay_alpha = 0.7
            
            # Calculate overlay region dimensions
            overlay_height = 200
            overlay_width = min(400, width - 20)  # Max width with padding
            
            # Create semi-transparent background for text
            overlay_region = np.zeros((overlay_height, overlay_width, 3), dtype=np.uint8)
            overlay_region[:] = (0, 0, 0)  # Black background
            
            # Info text
            info_lines = [
                f"Frame: {frame_count}/{total_frames}",
                f"Processed: {processed_frames}",
                f"Processing FPS: {current_fps:.1f}",
                f"Inference: {avg_inference:.1f}ms",
                f"Front Detections: {filtered_detections}",
                f"Alerts: {len(alert_history)}"
            ]
            
            y_offset = 25
            for i, text in enumerate(info_lines):
                cv2.putText(
                    overlay_region,
                    text,
                    (10, y_offset + i * 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )
            
            # Show recent alerts
            if alerts:
                alert_text = f"ALERT: {alerts[0]['from'].upper()} -> {alerts[0]['to'].upper()}"
                cv2.putText(
                    overlay_region,
                    alert_text,
                    (10, overlay_height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )
            
            # Blend overlay region onto frame
            x_start = 10
            y_start = 10
            x_end = x_start + overlay_width
            y_end = y_start + overlay_height
            
            # Ensure we don't go out of bounds
            if y_end <= height and x_end <= width:
                # Blend the overlay region with the frame
                frame_region = frame[y_start:y_end, x_start:x_end].copy()
                blended_region = cv2.addWeighted(frame_region, 1.0 - overlay_alpha, overlay_region, overlay_alpha, 0)
                frame[y_start:y_end, x_start:x_end] = blended_region
            
            # Write frame (if saving and frame was processed)
            # Always write original resolution for output video
            if save_output and should_process and out is not None:
                out.write(frame)
            
            # Show preview (resize for display only, doesn't affect performance)
            if show_preview:
                # Resize frame for display (maintains aspect ratio, fits on screen)
                display_frame = cv2.resize(frame, (display_width, display_height), interpolation=cv2.INTER_LINEAR)
                cv2.imshow('Real-Time Traffic Light Detection - Approach 2 V2', display_frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n⚠️  Processing stopped by user")
                    break
                elif key == ord('p'):
                    paused = True
                    print("⏸️  Paused (press 'p' to resume)")
    
    except KeyboardInterrupt:
        print("\n⚠️  Processing interrupted by user")
    
    finally:
        # Cleanup
        cap.release()
        if out is not None:
            out.release()
        if show_preview:
            cv2.destroyAllWindows()
        
        # Final statistics
        total_processing_time = time.time() - start_time
        avg_fps = processed_frames / total_processing_time if total_processing_time > 0 else 0
        avg_inference = np.mean(inference_times) if inference_times else 0
        min_inference = np.min(inference_times) if inference_times else 0
        max_inference = np.max(inference_times) if inference_times else 0
        
        print("\n" + "=" * 70)
        print("✅ Processing Complete!")
        print("=" * 70)
        print(f"\n⏱️  Performance Metrics:")
        print(f"   Total Time: {total_processing_time:.1f}s")
        print(f"   Total Frames: {frame_count}")
        print(f"   Processed Frames: {processed_frames}")
        print(f"   Average Processing FPS: {avg_fps:.1f}")
        print(f"   Average Inference Time: {avg_inference:.2f}ms")
        if inference_times:
            print(f"   Min Inference Time: {min_inference:.2f}ms")
            print(f"   Max Inference Time: {max_inference:.2f}ms")
        
        print(f"\n🎯 Detection Statistics:")
        print(f"   Total Detections (after filter): {filtered_detections}")
        if processed_frames > 0:
            print(f"   Average per Processed Frame: {filtered_detections/processed_frames:.2f}")
        
        if detection_stats:
            print(f"\n📊 Detections by Class (Front-Only):")
            for cls_name, count in sorted(detection_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = count / filtered_detections * 100 if filtered_detections > 0 else 0
                print(f"   {cls_name}: {count} ({percentage:.1f}%)")
        
        if alert_history:
            print(f"\n🚨 Alert Summary:")
            print(f"   Total Alerts: {len(alert_history)}")
            print(f"   Recent Alerts:")
            for alert in alert_history[-5:]:  # Show last 5 alerts
                print(f"      {alert['from'].upper()} -> {alert['to'].upper()}")
        
        if save_output:
            print(f"\n💾 Output saved: {output_path}")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description='Real-time video processing with Approach 2 Traffic Light Detection (V2 - Front-Only)'
    )
    parser.add_argument(
        '--input', '-i',
        type=str,
        default='../trafficv2.mp4',
        help='Input video file path (default: ../trafficv2.mp4)'
    )
    parser.add_argument(
        '--model', '-m',
        type=str,
        choices=['nano', 'small', 'medium'],
        default='nano',
        help='Model size to use: nano, small, or medium (default: nano)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='output_realtime_v2.mp4',
        help='Output video file path (default: output_realtime_v2.mp4)'
    )
    parser.add_argument(
        '--conf', '-c',
        type=float,
        default=0.25,
        help='Confidence threshold (0-1, default: 0.25)'
    )
    parser.add_argument(
        '--target-fps', '-f',
        type=int,
        default=10,
        help='Target processing FPS (default: 10)'
    )
    parser.add_argument(
        '--no-preview',
        action='store_true',
        help='Disable live preview window'
    )
    parser.add_argument(
        '--save',
        action='store_true',
        help='Save output video (default: preview only, no save)'
    )
    parser.add_argument(
        '--center-margin',
        type=float,
        default=0.3,
        help='Margin from edges for front detection (0.3 = center 40%%, default: 0.3)'
    )
    parser.add_argument(
        '--top-portion',
        type=float,
        default=0.6,
        help='Top portion of frame to consider (0.6 = top 60%%, default: 0.6)'
    )
    
    args = parser.parse_args()
    
    # Map model name to file path
    model_map = {
        'nano': 'models/best_traffic_nano_yolo.pt',
        'small': 'models/best_traffic_small_yolo.pt',
        'medium': 'models/best_traffic_med_yolo_v8.pt'
    }
    
    model_path = model_map[args.model]
    
    # Check if input file exists
    if not Path(args.input).exists():
        print(f"❌ Error: Input video file not found: {args.input}")
        print(f"   Please provide a valid video file path.")
        return
    
    # Process video
    process_video_realtime(
        video_path=args.input,
        model_path=model_path,
        output_path=args.output,
        conf_threshold=args.conf,
        target_fps=args.target_fps,
        show_preview=not args.no_preview,
        save_output=args.save,  # Default False, only save if --save flag is used
        center_margin=args.center_margin,
        top_portion=args.top_portion
    )


if __name__ == '__main__':
    main()

