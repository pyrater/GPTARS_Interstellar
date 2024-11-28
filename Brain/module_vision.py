from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import subprocess
import os
import traceback

def describe_camera_view(save_path: str = "captured_image.jpg") -> str:
    """
    Capture an image using libcamera-still and generate a descriptive caption using BLIP.
    """
    try:
        print("Initializing BLIP model and processor...")
        # Initialize BLIP model and processor
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

        print("Capturing image using libcamera-still...")
        # Use libcamera-still to capture an image
        command = [
            "libcamera-still",
            "-o", save_path,
            "--timeout", "1000"  # 1-second timeout for capture
        ]
        subprocess.run(command, check=True)

        # Verify the image was captured
        if not os.path.exists(save_path):
            return f"Error: Image capture failed. File {save_path} does not exist."

        # Open the captured image with PIL
        image = Image.open(save_path)

        print("Generating caption...")
        # Generate a caption
        inputs = processor(image, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=100)
        caption = processor.decode(outputs[0], skip_special_tokens=True)

        print("Caption generated:", caption)
        # Return the caption
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
