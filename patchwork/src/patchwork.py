import base64
from openai import OpenAI
import os
import sys
from dotenv import load_dotenv
import tiktoken
from PIL import Image
import json
import anthropic
# Load environment variables from the .env file
from utils import formatOutput
from utils import generateWordCloud
from utils import move_files_to_date_folder
from datetime import datetime
load_dotenv()
client = anthropic.Anthropic(api_key=os.environ["CLAUDE_API"])
MODEL = "claude-3-5-sonnet-20241022"
IMAGE_MEDIA_TYPE = "image/jpeg"

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

# Function to analyze content -
def analyze(content):
    response = client.messages.create(
        model=MODEL,
        max_tokens=8191,
        messages=[{"role": "user", "content": content}]
    )
    return str(response.content[0].text)


def analyze_report(content):
    response = client.messages.create(
        model=MODEL,
        max_tokens=8191,
        messages= [
        {"role": "user", "content": """Create a comprehensive report in JSON format with the following JSON structure but add as many issues and recommendations as you see fit:
         
        After summarizing all screenshots, aggregate the information into a cohesive report. Consider the following aspects:

   a. Mental health check:
      - Is the user exhibiting signs of doom scrolling?
      - Are there indications of anxiety or stress in their browsing patterns?
      - Is there a healthy balance between work and leisure activities?

   b. Productivity analysis:
      - Is the user getting distracted from work-related tasks?
      - How much time is spent on productive vs. non-productive activities?
      - Are there frequent context switches or multitasking behaviors?

   c. Social media and platform usage:
      - Which social media platforms or websites are most frequently used?
      - How much time is spent on each platform?
      - Are there any concerning patterns in social media usage?

4. Perform entity extraction to provide more context into how the user spends their time. Identify and list:
   - Applications used
   - Websites visited
   - Topics of interest
   - People or accounts interacted with

5. Based on your analysis, provide recommendations on how the user could improve their relationship with various platforms and social media in general.

6. Your final report should include as many recommendations as you see fit, the below is just an example please change the content to fit the user summary.
         
All recommendations should be directed towards the user in the you tone.
         
Descriptions length should be 4-5 sentences. Descriptions for each issue, pattern and recommendation should be unique. ALWAYS add 3-4 sentences to each description.
         
JSON FORMAT THAT YOU NEED TO FOLLOW:
         {
  "content_analysis": {
    "word_cloud_counts": {
        "EXAMPLE1": 10,
        "EXAMPLE2": 20,
        "EXAMPLE3": 30,
        "EXAMPLE4": 40
    },
    "summary": "<Summary of the usage>",
  "overall_wellness_score": 70
         },
  "problematic_usage_patterns": {
    "issues": [
      {
        "issue": "<Issue Tilte>",
        "description": "<Description of the Issue>"
      },
      {
        "issue": "<Issue Tilte>",
        "description": "<Description of the Issue>"
      },
      {
        "issue": "<Issue Tilte>",
        "description": "<Description of the Issue>"
      }
         // Add more recommendations as needed
    ]
  },
  "positive_usage": {
    "patterns": [
      {
        "pattern": "<Pattern Title>",
        "description": <Description of the Pattern
      },
      {
        "pattern": "<Pattern Title>",
        "description": <Description of the Pattern
      },
      {
        "pattern": "<Pattern Title>",
        "description": <Description of the Pattern
      }
         // Add more recommendations as needed
    ]
  },
  "recommendations": {
    "suggestions": [
      {
        "recommendation": "<Recommendation Title",
        "details": "<Description of recommencation>"
      },
      {
        "recommendation": "<Recommendation Title",
        "details": "<Description of recommencation>"
      },
      {
        "recommendation": "<Recommendation Title",
        "details": "<Description of recommencation>"
      }
         // Add more recommendations as needed
    ]
  }
}"""},
        {"role": "user", "content": content},
    ]
    )

    return str(response.content[0].text)


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
        "text": "You are an AI assistant tasked with analyzing a series of 10 screenshots taken at 1-minute intervals from a user's computer. Your goal is to summarize these screenshots and create a comprehensive summary on the user's computer usage, focusing on mental health, productivity, and social media habits, as well as entity extraction and recommendations.",
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
                "type": "image",
                "source": {
                        "type": "base64",
                        "media_type": IMAGE_MEDIA_TYPE,
                        "data": base64_image,
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
        return comprehensive_analysis
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


    comprehensive_analysis = process_directory(directory)
    print(comprehensive_analysis)
    # Convert comprehensive_analysis to a JSON string
    analysis_json = json.dumps(comprehensive_analysis, indent=2)
    print(analysis_json)
    # Convert JSON string to a plain text string
    analysis_text = json.loads(analysis_json)
    analysis_string = str(analysis_text)
    report = analyze_report(analysis_string)
    print(report)
    print(type(report))
    # Convert the report string to a JSON object
    # Define the output file name
    output_file = "report.json"

    # Write the report to the output file
    with open(output_file, "w") as f:
        f.write(report)
    
    formatOutput(output_file)
    generateWordCloud(output_file,"output.png")
    move_files_to_date_folder(datetime.now().strftime("%Y-%m-%d"))

    print(f"Tech usage report has been saved to {output_file}")