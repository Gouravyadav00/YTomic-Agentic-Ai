import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline
import re

# Download required NLTK data
nltk.download('punkt')
nltk.download('vader_lexicon')

class MotivationalQuoteFinder:
    def __init__(self):
        # Initialize sentiment analyzer
        self.sia = SentimentIntensityAnalyzer()
        # Initialize zero-shot classification pipeline
        self.classifier = pipeline("zero-shot-classification",
                                 model="facebook/bart-large-mnli")
        
    def load_data(self, csv_path):
        """Load and preprocess the transcript data"""
        df = pd.read_csv(csv_path)
        # Clean the text column
        df['text'] = df['0'].str[7:]  # Remove timestamp prefix
        return df
    
    def is_motivational(self, text):
        """Determine if a text segment is motivational using multiple criteria"""
        # Check sentiment
        sentiment = self.sia.polarity_scores(text)
        
        # Use zero-shot classification to check if it's motivational
        candidate_labels = ["motivational", "informative", "casual"]
        result = self.classifier(text, candidate_labels)
        
        # Combine sentiment and classification scores
        is_motivational = (
            sentiment['compound'] > 0.3 and  # Positive sentiment
            result['labels'][0] == 'motivational' and  # Classified as motivational
            result['scores'][0] > 0.5  # High confidence in classification
        )
        
        return is_motivational
    
    def find_motivational_quotes(self, df):
        """Find motivational quotes and their timestamps"""
        motivational_quotes = []
        
        # Process each row
        for idx, row in df.iterrows():
            text = row['text']
            if pd.isna(text):
                continue
                
            # Check if the text is motivational
            if self.is_motivational(text):
                quote_info = {
                    'quote': text,
                    'start_time': row['start'],
                    'end_time': row['stop'],
                    'sentiment_score': self.sia.polarity_scores(text)['compound']
                }
                motivational_quotes.append(quote_info)
        
        return motivational_quotes

def main():
    # Initialize the quote finder
    quote_finder = MotivationalQuoteFinder()
    
    # Load the data
    df = quote_finder.load_data("Data.csv")
    
    # Find motivational quotes
    motivational_quotes = quote_finder.find_motivational_quotes(df)
    
    # Print results
    print("\nFound Motivational Quotes:")
    print("-" * 50)
    for quote in motivational_quotes:
        print(f"\nQuote: {quote['quote']}")
        print(f"Time: {quote['start_time']} - {quote['end_time']}")
        print(f"Sentiment Score: {quote['sentiment_score']:.2f}")
        print("-" * 50)

if __name__ == "__main__":
    main() 