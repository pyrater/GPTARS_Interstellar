# ENVSETUP.md

## Hardware Prerequisites

1. **PC with NVIDIA GPU**:
   - Ensure you have a PC with an NVIDIA GPU available for running the server.

2. **Raspberry Pi 5**:
   - The Raspberry Pi 5 will act as a client, sending TTS requests to the XTTS server running on the PC.

---

## Step-by-Step Guide (WINDOWS ONLY)

### 1. Prepare Your PC with NVIDIA GPU
The TTS server must run on your GPU-enabled PC due to its computational requirements.

1. Ensure **Python 3.9-3.12** is installed on your PC.
2. Install **CUDA** and **cuDNN** compatible with your NVIDIA GPU - [CUDA Installation](https://www.youtube.com/watch?v=krAUwYslS8E)
3. Install **PyTorch** compatible with your CUDA and cuDNN versions - [PyTorch Installation](https://pytorch.org/get-started/locally/)

### 2. Set Up XTTS API Server

#### Clone the XTTS API Server Repository
Run the following command to clone the [XTTS API Server repository](https://github.com/daswer123/xtts-api-server):

```bash
git clone https://github.com/daswer123/xtts-api-server.git
```

#### Install XTTS API Server
Follow the installation guide for your operating system:
- **Windows**:
  1. Create and activate a virtual environment:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
  2. Install the required packages:
     ```bash
     pip install xtts-api-server
     pip install torch==2.1.1+cu118 torchaudio==2.1.1+cu118 --index-url https://download.pytorch.org/whl/cu118
     ```

For more details, refer to the official [XTTS API Server Installation Guide](https://github.com/daswer123/xtts-api-server/tree/main).

---

#### Add the TARS.wav Speaker File
1. Download the `TARS-short.wav` and `TARS-long.wav` files from the `GPTARS_Interstellar` repository.
2. Place it in the `speakers/` directory within the XTTS project folder. If the directory does not exist, create it.

