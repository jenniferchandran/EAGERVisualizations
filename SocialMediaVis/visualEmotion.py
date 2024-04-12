import csv
from collections import defaultdict

def process_csv(input_file, output_file):
    # Initialize a dictionary to hold counts for each emotion per _Count column
    emotion_counts = defaultdict(lambda: defaultdict(int))

    with open(input_file, mode='r') as file:
        reader = csv.DictReader(file)
        
        # Iterate through each row in the CSV
        for row in reader:
            for key in row:
                # Check if the key ends with '_Count' and its value is '1'
                if key.endswith('_Count') and row[key] == '1':
                    # Increment the count for the respective emotion_label
                    emotion_counts[key][row['emotion_label']] += 1

    # Write the results to a new CSV file
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(['Count_Column', 'Emotion', 'Count'])

        # Write the counts for each emotion per _Count column
        for count_col, emotions in emotion_counts.items():
            for emotion, count in emotions.items():
                writer.writerow([count_col, emotion, count])

# Example usage
process_csv('fri_analyzed.csv', 'output.csv')