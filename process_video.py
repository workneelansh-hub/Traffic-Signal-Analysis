"""
Video Processing Script for Approach 2 - Traffic Light Detection
Processes video files and generates output with detection results and timing metrics.
"""

import cv2
import argparse
import time
from pathlib import Path
from ultralytics import YOLO
from collections import defaultdict
import numpy as np


def process_video_approach2(
    video_path,
    model_path='models/best_traffic_nano_yolo.pt',
    output_path='output_approach2.mp4',
    conf_threshold=0.25,
    show_preview=False
):
    """
    Process video file with YOLOv8 traffic light detection model.
    
    Args:
        video_path: Path to input video file
        model_path: Path to YOLOv8 model (.pt file)
        output_path: Path to save output video
        conf_threshold: Confidence threshold for detections (0-1)
        show_preview: Whether to show live preview window
    """
    
    print("=" * 70)
    print("Approach 2: Traffic Light Detection - Video Processing")
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
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"\n📊 Video Information:")
    print(f"   Resolution: {width}x{height}")
    print(f"   FPS: {fps}")
    print(f"   Total Frames: {total_frames}")
    print(f"   Duration: {total_frames/fps:.1f}s")
    
    # Video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Statistics
    frame_count = 0
    total_detections = 0
    inference_times = []
    total_processing_time = 0
    detection_stats = defaultdict(int)
    
    start_time = time.time()
    last_print_time = start_time
    
    print(f"\n🚀 Processing started...\n")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Run inference
            inference_start = time.time()
            results = model.predict(
                frame,
                conf=conf_threshold,
                verbose=False,
                imgsz=640
            )
            inference_time = (time.time() - inference_start) * 1000  # Convert to ms
            inference_times.append(inference_time)
            
            # Process results
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
            
            # Add FPS and timing info to frame
            avg_inference_time = np.mean(inference_times[-30:]) if len(inference_times) > 0 else 0
            current_fps = 1000 / avg_inference_time if avg_inference_time > 0 else 0
            
            # Draw info overlay
            info_text = [
                f"Frame: {frame_count}/{total_frames}",
                f"FPS: {current_fps:.1f}",
                f"Inference: {avg_inference_time:.1f}ms",
                f"Detections: {total_detections}"
            ]
            
            y_offset = 30
            for i, text in enumerate(info_text):
                cv2.putText(
                    frame,
                    text,
                    (10, y_offset + i * 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )
            
            # Write frame
            out.write(frame)
            
            # Show preview if requested
            if show_preview:
                cv2.imshow('Approach 2 - Traffic Light Detection', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n⚠️  Processing stopped by user")
                    break
            
            # Progress update every 2 seconds
            current_time = time.time()
            if current_time - last_print_time >= 2.0:
                elapsed = current_time - start_time
                progress = frame_count / total_frames * 100
                processing_fps = frame_count / elapsed
                eta = (total_frames - frame_count) / processing_fps if processing_fps > 0 else 0
                
                print(f"Progress: {frame_count}/{total_frames} ({progress:.1f}%) | "
                      f"FPS: {processing_fps:.1f} | "
                      f"Avg Inference: {avg_inference_time:.1f}ms | "
                      f"Detections: {total_detections} | "
                      f"ETA: {eta:.0f}s")
                
                last_print_time = current_time
    
    except KeyboardInterrupt:
        print("\n⚠️  Processing interrupted by user")
    
    finally:
        # Cleanup
        cap.release()
        out.release()
        if show_preview:
            cv2.destroyAllWindows()
        
        # Final statistics
        total_processing_time = time.time() - start_time
        avg_fps = frame_count / total_processing_time
        avg_inference = np.mean(inference_times) if inference_times else 0
        min_inference = np.min(inference_times) if inference_times else 0
        max_inference = np.max(inference_times) if inference_times else 0
        
        print("\n" + "=" * 70)
        print("✅ Processing Complete!")
        print("=" * 70)
        print(f"\n⏱️  Performance Metrics:")
        print(f"   Total Time: {total_processing_time:.1f}s")
        print(f"   Frames Processed: {frame_count}")
        print(f"   Average FPS: {avg_fps:.1f}")
        print(f"   Average Inference Time: {avg_inference:.2f}ms")
        print(f"   Min Inference Time: {min_inference:.2f}ms")
        print(f"   Max Inference Time: {max_inference:.2f}ms")
        print(f"   Processing Speed: {frame_count/total_processing_time:.2f}x real-time")
        
        print(f"\n🎯 Detection Statistics:")
        print(f"   Total Detections: {total_detections}")
        print(f"   Average per Frame: {total_detections/frame_count:.2f}" if frame_count > 0 else "   Average per Frame: 0")
        
        if detection_stats:
            print(f"\n📊 Detections by Class:")
            for cls_name, count in sorted(detection_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = count / total_detections * 100 if total_detections > 0 else 0
                print(f"   {cls_name}: {count} ({percentage:.1f}%)")
        
        print(f"\n💾 Output saved: {output_path}")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description='Process video with Approach 2 Traffic Light Detection'
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
        default='output_approach2.mp4',
        help='Output video file path (default: output_approach2.mp4)'
    )
    parser.add_argument(
        '--conf', '-c',
        type=float,
        default=0.25,
        help='Confidence threshold (0-1, default: 0.25)'
    )
    parser.add_argument(
        '--preview', '-p',
        action='store_true',
        help='Show live preview window during processing'
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
    process_video_approach2(
        video_path=args.input,
        model_path=model_path,
        output_path=args.output,
        conf_threshold=args.conf,
        show_preview=args.preview
    )


if __name__ == '__main__':
    main()

