import pandas as pd
import re

def convert_text_to_csv(input_file, output_file):
    try:
        # Read the text file
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Process the data
        data = []
        for line in lines:
            # Remove any extra whitespace and split by common delimiters
            line = line.strip()
            if line:  # Skip empty lines
                # Try to split by common delimiters (comma, tab, or multiple spaces)
                if ',' in line:
                    row = [item.strip() for item in line.split(',')]
                elif '\t' in line:
                    row = [item.strip() for item in line.split('\t')]
                else:
                    # Split by multiple spaces
                    row = re.split(r'\s{2,}', line)
                
                data.append(row)

        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        print(f"Successfully converted {input_file} to {output_file}")
        
        return df

    except Exception as e:
        print(f"Error converting file: {str(e)}")
        return None

if __name__ == "__main__":
    input_file = "Ai-Model/Data.txt"
    output_file = "Data.csv"
    df = convert_text_to_csv(input_file, output_file) 