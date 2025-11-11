# Step-by-Step Guide to Run Approach 2

## 📋 Prerequisites Checklist

- [ ] Python 3.8 or higher installed
- [ ] pip package manager available
- [ ] Video file to process (optional, for video processing)
- [ ] Webcam (optional, for live testing)

## 🚀 Step-by-Step Instructions

### Step 1: Navigate to Approach 2 Directory

Open terminal/command prompt and navigate to the Approach 2 folder:

```bash
cd "Approach 2"
```

**Windows PowerShell:**
```powershell
cd "Approach 2"
```

**Windows CMD:**
```cmd
cd "Approach 2"
```

**macOS/Linux:**
```bash
cd "Approach 2"
```

### Step 2: Create Virtual Environment (Recommended)

Creating a virtual environment isolates dependencies and prevents conflicts.

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

You should see `(venv)` in your terminal prompt after activation.

### Step 3: Install Required Packages

Install all dependencies from requirements.txt:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected output:**
```
Collecting ultralytics...
Collecting torch...
...
Successfully installed ...
```

**Installation time:** 2-5 minutes (depending on internet speed)

### Step 4: Verify Installation

Test that everything is installed correctly:

```bash
python -c "from ultralytics import YOLO; print('✅ Installation successful!')"
```

**Expected output:**
```
✅ Installation successful!
```

### Step 5: Test with Example Scripts

#### Option A: Test on Image (Quick Test)

```bash
python examples/Example.py
```

This will:
- Download a test image from the internet
- Run detection
- Display and save results

#### Option B: Test with Webcam (Live Test)

```bash
python "examples/Webcam Example.py"
```

This will:
- Open your webcam
- Show live detection
- Press 'q' to quit

### Step 6: Process Video File

Process a video file with detailed timing metrics:

```bash
python process_video.py --input ../trafficv2.mp4 --model nano --output output_approach2.mp4
```

**Command breakdown:**
- `--input ../trafficv2.mp4`: Input video (one folder up from Approach 2)
- `--model nano`: Use nano model (fastest)
- `--output output_approach2.mp4`: Output filename

**Other model options:**
- `--model nano`: Fastest (~44ms/frame)
- `--model small`: Balanced (~72ms/frame)
- `--model medium`: Most accurate (~130ms/frame)

**With preview window:**
```bash
python process_video.py --input ../trafficv2.mp4 --model nano --preview
```

## 📊 Understanding the Output

After processing, you'll see:

```
======================================================================
✅ Processing Complete!
======================================================================

⏱️  Performance Metrics:
   Total Time: 45.3s
   Frames Processed: 900
   Average FPS: 19.9
   Average Inference Time: 43.7ms
   Min Inference Time: 38.2ms
   Max Inference Time: 52.1ms
   Processing Speed: 0.66x real-time

🎯 Detection Statistics:
   Total Detections: 234
   Average per Frame: 0.26

📊 Detections by Class:
   traffic_light: 234 (100.0%)

💾 Output saved: output_approach2.mp4
======================================================================
```

## 🎯 Common Use Cases

### Use Case 1: Quick Test (Fastest)
```bash
python process_video.py -i ../trafficv2.mp4 -m nano
```

### Use Case 2: Best Quality
```bash
python process_video.py -i ../trafficv2.mp4 -m medium -o best_quality.mp4
```

### Use Case 3: Balanced Performance
```bash
python process_video.py -i ../trafficv2.mp4 -m small -c 0.3
```

### Use Case 4: Watch While Processing
```bash
python process_video.py -i ../trafficv2.mp4 -m nano -p
```

## 🔧 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'ultralytics'"

**Solution:**
```bash
pip install ultralytics
```

### Problem: "Could not open video file"

**Solution:**
- Check file path is correct
- Use relative path: `../trafficv2.mp4` (one folder up)
- Or absolute path: `C:/path/to/video.mp4`
- Ensure video file exists

### Problem: "Out of memory" or very slow

**Solution:**
- Use nano model: `--model nano`
- Process shorter video clips
- Close other applications

### Problem: CUDA/GPU not working

**Solution:**
- Check GPU: `nvidia-smi` (Windows/Linux)
- Install CUDA PyTorch:
  ```bash
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
  ```
- Note: CPU works fine, just slower

### Problem: Preview window not showing

**Solution:**
- Add `--preview` flag
- Ensure you have display/GUI access
- On remote servers, preview may not work

## 📈 Performance Tips

1. **For Speed**: Use `nano` model
2. **For Accuracy**: Use `medium` model
3. **For Balance**: Use `small` model
4. **GPU Available**: Automatically used if detected
5. **Lower Confidence**: Use `--conf 0.3` for more detections

## ✅ Verification Checklist

After setup, verify:

- [ ] Dependencies installed (`pip list | grep ultralytics`)
- [ ] Example script runs (`python examples/Example.py`)
- [ ] Video processing works (`python process_video.py --help`)
- [ ] Output video generated successfully
- [ ] Performance metrics displayed correctly

## 📚 Next Steps

- Read `SETUP.md` for detailed information
- Check `QUICK_START.md` for quick reference
- Review `README.md` for original repository info
- Experiment with different models and confidence thresholds

## 🆘 Getting Help

If you encounter issues:

1. Check error messages carefully
2. Verify all dependencies are installed
3. Ensure video file path is correct
4. Try with nano model first (fastest)
5. Check Python version: `python --version` (should be 3.8+)

