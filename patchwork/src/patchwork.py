import base64
from openai import OpenAI
import os
import sys
from dotenv import load_dotenv
import tiktoken

# Load environment variables from the .env file
load_dotenv()
client = OpenAI()
MODEL = "gpt-4o"
# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


# Getting the base64 string
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



def process_directory(directory_path):
    """Process all images in the directory and analyze mental health impact."""
    texts = [{
            "type": "text",
            "text": "Based on all these images, can you tell how this screen time is influencing the user",
            }]
    tokens = 0
    encoder = tiktoken.encoding_for_model(MODEL)
    # Load all image files from the directory
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
            image_path = os.path.join(directory_path, filename)
            base64_image = encode_image(image_path)
            num_tokens = encoder.encode(base64_image)
            tokens += len(num_tokens)
            texts.append({
            "type": "image_url",
            "image_url": {
                "url":  f"data:image/jpeg;base64,{base64_image}"
            }
            })
    print(f"Number of tokens used {tokens}")
    if len(texts) > 1:
        print("Analyzing extracted text for mental health impact...")
        # analysis = analyze(texts)
        print("\n--- Mental Health Impact Analysis ---")
        # print(analysis)
    else:
        print("No images from this file.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python patchwork.py <directory_path>")
        sys.exit(1)

    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        sys.exit(1)

    process_directory(directory)