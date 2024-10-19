import base64
from openai import OpenAI
import os
import sys
from dotenv import load_dotenv
import tiktoken
from PIL import Image

# Load environment variables from the .env file
load_dotenv()
client = OpenAI()
MODEL = "gpt-4o"

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
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": content
            }
        ],
    )
    return response.choices[0].message.content

# Function to process all images in a directory
def process_directory(directory_path):
    """Process all images in the directory, compress them, and analyze their mental health impact."""
    texts = [{
        "type": "text",
        "text": "Based on all these images, can you tell how this screen time is influencing the user",
    }]
    tokens = 0
    encoder = tiktoken.encoding_for_model(MODEL)

    # Load and compress all image files from the directory
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
            image_path = os.path.join(directory_path, filename)
            print(f"Loading image.... {image_path}")

            # Compress the image
            compressed_image_path = compress_image(image_path)
            print(f"Compressed image.... {image_path}")
            # Encode the compressed image
            base64_image = encode_image(compressed_image_path)

            # Count tokens
            num_tokens = encoder.encode(base64_image)
            tokens += len(num_tokens)

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

    print(f"Number of tokens used {tokens}")
    if len(texts) > 1:
        print("Analyzing extracted text for mental health impact...")
        # analysis = analyze(texts)
        print("\n--- Mental Health Impact Analysis ---")
        # print(analysis)
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
