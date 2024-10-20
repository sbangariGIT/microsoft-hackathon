import base64
from openai import OpenAI
import os
import sys
from dotenv import load_dotenv
import tiktoken
from PIL import Image
import requests

# Load environment variables from the .env file
load_dotenv()
# client = OpenAI()
MODEL = "gpt-4o-mini"
encoder = tiktoken.encoding_for_model(MODEL)

url = "https://api.portkey.ai/v1/chat/completions"


headers = {
    "x-portkey-api-key": os.getenv("PORTKEY_API_KEY"),
    "x-portkey-virtual-key": os.getenv("PORTKEY_VIRTUAL_KEY"),
    "Content-Type": "application/json"
}

# Function to compress the image without losing much quality
def compress_image(image_path, max_size=(1024, 1024), quality=85):
    """
    Compresses an image by resizing it and saving with a lower quality.
    Args:
        image_path (str): Path to the image to be compressed.
        max_size (tuple): Maximum width and height for the resized image.
        quality (int): Quality of the output image (1 to 100). Default is 85.
    Returns:
        compressed_image_path (str): Path to the compressed image.
    """
    img = Image.open(image_path)

    # Convert image to RGB if it's RGBA (to remove alpha channel)
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    # Resize image while maintaining aspect ratio
    img.thumbnail(max_size)

    # Save the image in JPEG format with the given quality
    compressed_image_path = f"compressed_{os.path.basename(image_path)}"
    img.save(compressed_image_path, format="JPEG", quality=quality)

    return compressed_image_path

# Function to encode the image in base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to analyze content
def analyze(content):
    payload = {
    "messages": [
        {"role": "user", "content": content}
    ],
    "model": MODEL
    }
    response = requests.post(url, headers=headers, json=payload)

    return response.json()["choices"][0]["message"]["content"]

def create_batches(images):
    batches = []
    batch_size = 10
    for i in range(0, len(images), batch_size):
        batch = images[i:i + batch_size]  # Create a batch of 10 images
        batches.append(batch)             # Add the batch to the batches list
    return batches

def run_analysis_on_batch(batch):
    texts = [{
        "type": "text",
        "text": "You are an AI assistant tasked with analyzing a series of 10 screenshots taken at 1-minute intervals from a user's computer. Your goal is to summarize these screenshots and create a comprehensive report on the user's computer usage, focusing on mental health, productivity, and social media habits",
    }]
    for image_path in batch:
            print(f"Loading image.... {image_path}")
            # Compress the image
            compressed_image_path = compress_image(image_path)
            print(f"Compressed image.... {image_path}")
            # Encode the compressed image
            base64_image = encode_image(compressed_image_path)
            # Append to texts
            texts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })
            print(f"Appended image.... {image_path}")
            # Optionally delete the compressed image after use to save space
            os.remove(compressed_image_path)
    return analyze(texts)

def run_analysis_on_all(batches):
    comprehensive_analysis = {}
    batch_num = 1
    for batch in batches:
        print("Running analysis on batch " + str(batch_num))
        comprehensive_analysis["batch_" + str(batch_num)] = run_analysis_on_batch(batch)
        batch_num += 1
    return comprehensive_analysis

# Function to process all images in a directory
def process_directory(directory_path):
    """Process all images in the directory, compress them, and analyze their mental health impact."""
    images = []
    # Load and compress all image files from the directory
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
            image_path = os.path.join(directory_path, filename)
            print("image_path", image_path)
            images.append(image_path)
    print(images)
    if len(images) > 1:
        print("Analyzing extracted text for mental health impact...")
        batches = create_batches(images)
        comprehensive_analysis = run_analysis_on_all(batches)
        print("\n--- Mental Health Impact Analysis ---")
        print(comprehensive_analysis)
    else:
        print("No images from this directory.")




if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python patchwork.py <directory_path>")
        sys.exit(1)

    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        sys.exit(1)

    process_directory(directory)
