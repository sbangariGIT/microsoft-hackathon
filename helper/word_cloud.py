import wordcloud as wc

def run():
    word_cloud_counts = {
        "Social Media": 45,
        "Development": 38,
        "Python": 25,
        "YouTube": 20,
        "Mental Health": 18,
        "Flutter/Dart": 15,
        "API": 12,
        "Productivity": 10
    }
    
    if word_cloud_counts:
        # Create the WordCloud object with the specified settings
        word_cloud = wc.WordCloud(
            width=800, height=400, background_color="white"
        ).generate_from_frequencies(word_cloud_counts)

        # Save the word cloud to a PNG file
        word_cloud.to_file('output.png')
        print("Word cloud saved as output.png")
    else:
        print("No word cloud data found in the file.")

run()
