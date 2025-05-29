# setup_advanced_ai.py
# Run this script to set up the advanced AI system

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    
    # Basic packages
    packages = [
        "flask==2.3.3",
        "requests==2.31.0",
        "certifi==2023.7.22",
        "pytube==15.0.0",
        "youtube-transcript-api==0.6.1",
        "sentence-transformers==2.2.2",
        "scikit-learn==1.3.0",
        "numpy==1.24.3",
        "nltk==3.8.1",
        "pandas==2.0.3",
        "scipy==1.11.3"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}")
            print("Trying without version constraints...")
            try:
                package_name = package.split("==")[0]
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                print(f"✓ {package_name} installed successfully")
            except subprocess.CalledProcessError as e2:
                print(f"✗ Failed to install {package_name}: {e2}")

def download_nltk_data():
    """Download required NLTK data"""
    print("Downloading NLTK data...")
    
    import nltk
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✓ NLTK data downloaded successfully")
    except Exception as e:
        print(f"✗ Failed to download NLTK data: {e}")

def download_sentence_transformer():
    """Download sentence transformer model"""
    print("Downloading sentence transformer model...")
    
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ Sentence transformer model downloaded successfully")
    except Exception as e:
        print(f"✗ Failed to download sentence transformer: {e}")

def test_installation():
    """Test if everything is installed correctly"""
    print("Testing installation...")
    
    try:
        from advanced_ai_clip_generator import AdvancedAIClipGenerator
        generator = AdvancedAIClipGenerator()
        print("✓ Advanced AI Clip Generator imported successfully")
        
        # Test with sample text
        sample_transcript = """[00:05] The key to success is persistence and hard work
[00:10] Never give up on your dreams no matter what
[00:15] You have the power to change your life completely"""
        
        clips = generator.generate_advanced_clips(sample_transcript, max_clips=3)
        print(f"✓ Generated {len(clips)} test clips successfully")
        
        if clips:
            print("Sample clip:")
            clip = clips[0]
            print(f"  Text: {clip['text'][:60]}...")
            print(f"  Category: {clip['category']}")
            print(f"  Overall Score: {clip['overall_score']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Installation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("Advanced AI Clip Generator Setup")
    print("=" * 60)
    
    # Step 1: Install requirements
    install_requirements()
    print()
    
    # Step 2: Download NLTK data
    download_nltk_data()
    print()
    
    # Step 3: Download sentence transformer
    download_sentence_transformer()
    print()
    
    # Step 4: Test installation
    success = test_installation()
    print()
    
    print("=" * 60)
    if success:
        print("✓ Setup completed successfully!")
        print("You can now use the Advanced AI Clip Generator.")
    else:
        print("✗ Setup encountered some issues.")
        print("Please check the error messages above and try installing manually.")
    print("=" * 60)

if __name__ == "__main__":
    main()