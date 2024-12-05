# ENVSETUP.md

## Hardware Prerequisites

1. **PC with NVIDIA GPU**: Ensure you have a PC with an NVIDIA GPU available for running the server.

2. **Raspberry Pi 5**: The Raspberry Pi 5 will act as a client, sending TTS requests to the XTTS server running on the PC.

---

## Step-by-Step Guide (WINDOWS ONLY INSTRUCTIONS)

### 1. Prepare Your PC with NVIDIA GPU
The TTS server must run on your GPU-enabled PC due to its computational requirements.

1. Ensure **Python 3.9-3.12** is installed on your PC.
2. Install **CUDA** and **cuDNN** compatible with your NVIDIA GPU - [CUDA Installation](https://www.youtube.com/watch?v=krAUwYslS8E)
3. Install **PyTorch** compatible with your CUDA and cuDNN versions - [PyTorch Installation](https://pytorch.org/get-started/locally/)

### 2. Set Up XTTS API Server

#### C. Clone the XTTS API Server Repository
Run the following command to clone the [XTTS API Server repository](https://github.com/daswer123/xtts-api-server):

```bash
git clone https://github.com/daswer123/xtts-api-server.git
```

#### B. Install XTTS API Server
Follow the installation guide for your operating system:
- **Windows**:
  1. Create and activate a virtual environment:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
  2. Install xtts-api-server:
     ```bash
     pip install xtts-api-server
     ```

For more details, refer to the official [XTTS API Server Installation Guide](https://github.com/daswer123/xtts-api-server/tree/main).

#### C. Add the TARS.wav Speaker File
1. Download the `TARS-short.wav` and `TARS-long.wav` files from the `GPTARS_Interstellar` repository under `Brain/TTS/wakewords
/VoiceClones`. These will be the different voices you can use for TARS.
2. Place it in the `speakers/` directory within the XTTS project folder. If the directory does not exist, create it.

#### D. Start the XTTS API Server
1. Open a terminal in the `xtts-api-server` project directory.
2. Activate your virtual environment if not already active:
3. Start the XTTS API Server:
   ```bash
   python -m xtts_api_server
   ```

#### E. Open the API Documentation
1. Once the server is running, open a browser and navigate to:
   ```
   http://localhost:8020/docs
   ```
2. This will open the API's Swagger documentation interface, which you can use to test the server and its endpoints.

#### F. Verify the Available Speakers
1. Locate the **GET /speakers** endpoint in the API documentation.
2. Click **"Try it out"** and then **"Execute"** to test the endpoint.
3. Ensure the response includes the `TARS-Short` and `TARS-Long` speaker files, with entries similar to:
   ```json
   [
     {
       "name": "TARS-Long",
       "voice_id": "TARS-Long",
       "preview_url": "http://localhost:8020/sample/TARS-Long.wav"
     },
     {
       "name": "TARS-Short",
       "voice_id": "TARS-Short",
       "preview_url": "http://localhost:8020/sample/TARS-Short.wav"
     }
   ]
   ```

#### G. Test Text-to-Speech (TTS)
1. Locate the **POST /tts_to_audio** endpoint in the API documentation.
2. Click **"Try it out"** and input the following JSON in the **Request Body**:
   ```json
   {
       "text": "Hello, this is TARS speaking.",
       "speaker_wav": "TARS-Short",
       "language": "en"
   }
   ```
3. Click **"Execute"** to send the request.
4. Check the response for a generated audio file. You should see a download field where you can download and listen to the audio output.