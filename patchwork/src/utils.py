import os
import json
from wordcloud import WordCloud  # This now imports correctly from the library
import matplotlib.pyplot as plt
import shutil

def formatOutput(filename: str) -> None:
    # Step 1: Open the file in read mode
    with open(filename, "r") as file:
        lines = file.readlines()

    # Step 2: Remove the first and last lines
    if len(lines) > 2:
        lines = lines[1:-1]
    else:
        lines = []

    # Step 3: Open the same file in write mode
    with open(filename, "w") as file:
        file.writelines(lines)


def generateWordCloud(filename: str, output_image: str) -> None:
    # Step 1: Read the JSON file
    with open(filename, "r") as file:
        content = file.read()  # Read the raw content of the file
        try:
            data = json.loads(content)  # Attempt to load the JSON content
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")  # Handle and display JSON parsing error
            return

    # Step 2: Extract the 'word_cloud_counts' from the nested 'content_analysis' section
    word_cloud_counts = data.get("content_analysis", {}).get("word_cloud_counts", {})

    # Step 3: Generate the word cloud using WordCloud
    if word_cloud_counts:
        wordcloud = WordCloud(
            width=800, height=400, background_color="white"
        ).generate_from_frequencies(word_cloud_counts)

        # Step 4: Save the word cloud to a PNG file
        wordcloud.to_file(output_image)
        print(f"Word cloud saved as {output_image}")
    else:
        print("No word cloud data found in the file.")


def move_files_to_date_folder(date):
    # Get the user's home directory
    home_directory = os.path.expanduser("~")

    # Define the target directory path dynamically
    target_directory = os.path.join(
        home_directory, "Library/Containers/com.example.screensage/Data/reports", date
    )

    # Create the target directory if it doesn't exist
    os.makedirs(target_directory, exist_ok=True)

    # Define the files to move
    files_to_move = ["output.png", "report.json"]

    for file_name in files_to_move:
        # Construct the full path for the source file
        source_path = os.path.join(os.getcwd(), file_name)

        # Check if the file exists before attempting to move it
        if os.path.isfile(source_path):
            # Move the file to the target directory
            shutil.move(source_path, target_directory)
            print(f"Moved: {file_name} to {target_directory}")
        else:
            print(f"File not found: {file_name}")


def main():
    # Assuming 'test.json' contains the 'word_cloud_counts'
    # formatOutput("test.json")
    generateWordCloud("report.json","output.png")
    move_files_to_date_folder("2024-10-19")

if __name__ == "__main__":
    main()
