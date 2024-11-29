from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import subprocess
import os
import traceback
import time
import torch

# Global variables for the model and processor
processor = None
model = None
device = torch.device('cpu')  # Explicitly set device to CPU

def initialize_model():
    global processor, model
    if processor is None or model is None:
        print("Initializing BLIP model and processor...")
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

        # Move model to CPU (redundant since it's already on CPU, but included for clarity)
        model.to(device)

        # Apply dynamic quantization to speed up CPU inference
        model = torch.quantization.quantize_dynamic(
            model, {torch.nn.Linear}, dtype=torch.qint8
        )

        print("BLIP model and processor initialized.")

def describe_camera_view(save_path: str = "captured_image.jpg") -> str:
    """
    Capture an image using libcamera-still and generate a descriptive caption using BLIP.
    """
    try:
        start_time = time.time()
        initialize_model()  # Ensure the model is initialized
        model_init_time = time.time()
        print(f"Model initialization time: {model_init_time - start_time:.2f} seconds")

        print("Capturing image using libcamera-still...")
        # Use libcamera-still to capture an image
        command = [
            "libcamera-still",
            "-o", save_path,
            "--timeout", "300",  # 0.3-second timeout for capture
            "--width", "320",
            "--height", "240"
        ]
        subprocess.run(command, check=True)
        image_capture_time = time.time()
        print(f"Image capture time: {image_capture_time - model_init_time:.2f} seconds")

        # Verify the image was captured
        if not os.path.exists(save_path):
            return f"Error: Image capture failed. File {save_path} does not exist."

        # Open the captured image with PIL
        image = Image.open(save_path)
        # Optionally resize the image for speed (already captured at 320x240)
        # image = image.resize((320, 240))

        print("Generating caption...")
        # Generate a caption
        inputs = processor(image, return_tensors="pt")
        inputs = {key: value.to(device) for key, value in inputs.items()}
        inference_start_time = time.time()
        outputs = model.generate(**inputs, max_new_tokens=50, num_beams=1)
        inference_end_time = time.time()
        print(f"Model inference time: {inference_end_time - inference_start_time:.2f} seconds")

        caption = processor.decode(outputs[0], skip_special_tokens=True)

        print("Caption generated:", caption)
        end_time = time.time()
        total_time = end_time - start_time
        print(f"Total time taken: {total_time:.2f} seconds")
        return caption
    except subprocess.CalledProcessError as e:
        return f"Error: libcamera-still command failed with error {e}"
    except Exception as e:
        print("Error occurred:", traceback.format_exc())
        return f"Error: {e}"

# Example usage
if __name__ == "__main__":
    caption = describe_camera_view()
    print("Generated Caption:", caption)
