# Deepfake Benchmarking & Training Datasets

This folder is designed to house benchmark datasets for reproducible evaluation and training of the visual and acoustic forensic models.

## Recommended Benchmark Datasets

### 1. Visual Deepfakes (Images & Videos)
- **FaceForensics++ (FF++)**:
  - Contains 1,000 real YouTube video sequences manipulated with four state-of-the-art face manipulation methods: Deepfakes, Face2Face, FaceSwap, and NeuralTextures.
  - Provided at three compression rates: Raw (c0), High Quality (c23), and Low Quality (c40).
  - License: Academic Research License.
  - Access Request: [https://github.com/ondyari/FaceForensics](https://github.com/ondyari/FaceForensics)
- **Celeb-DF (v2)**:
  - 590 original YouTube videos of celebrities and 5,639 high-quality deepfake videos.
  - Reduced color mismatch and temporal artifacts compared to initial generation benchmarks.
  - Access: [https://github.com/yuezunli/celeb-deepfakeforensics](https://github.com/yuezunli/celeb-deepfakeforensics)
- **DiffusionDB / SynthWild**:
  - Large-scale prompt-to-image dataset for detecting modern Stable Diffusion, Midjourney, and DALL-E generative artifacts.

### 2. Audio & Speech Clones
- **ASVspoof 2021 (Logical Access Track)**:
  - Benchmark for detecting speech synthesis (TTS) and voice conversion (VC) artifacts across modern neural vocoders (HiFi-GAN, WaveNet, Tacotron).
  - License: CC BY 4.0.
  - Access: [https://www.asvspoof.org/](https://www.asvspoof.org/)

## Directory Structure for Local Training

```
datasets/
  train/
    authentic/
    manipulated/
  val/
    authentic/
    manipulated/
  test/
    authentic/
    manipulated/
```

To run training:
```bash
python -m app.ai_engine.training.train_image_model --data_dir ./datasets --epochs 15
```
