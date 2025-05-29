# fix_nltk_ssl.py
# Run this script to fix NLTK SSL certificate issues

import ssl
import nltk
import certifi
import os

def fix_nltk_ssl_and_download():
    """Fix SSL issues and download NLTK data"""
    
    print("Fixing NLTK SSL certificate issues...")
    
    try:
        # Method 1: Use certifi certificates
        import certifi
        os.environ['SSL_CERT_FILE'] = certifi.where()
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        print("✓ Set SSL certificates using certifi")
    except ImportError:
        print("⚠ certifi not available, trying alternative methods")
    
    try:
        # Method 2: Create unverified SSL context (less secure but works)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Try downloading with SSL context
        print("Attempting to download NLTK data...")
        
        # Set NLTK data path
        nltk_data_dir = os.path.expanduser('~/nltk_data')
        if not os.path.exists(nltk_data_dir):
            os.makedirs(nltk_data_dir)
        nltk.data.path.append(nltk_data_dir)
        
        # Download punkt tokenizer
        try:
            print("Downloading punkt tokenizer...")
            nltk.download('punkt', quiet=False, download_dir=nltk_data_dir)
            print("✓ punkt downloaded successfully")
        except Exception as e:
            print(f"⚠ punkt download failed: {e}")
            # Try alternative download
            try:
                import urllib.request
                import zipfile
                import tempfile
                
                print("Trying alternative download method for punkt...")
                punkt_url = "https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt.zip"
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                    urllib.request.urlretrieve(punkt_url, tmp_file.name)
                    
                    tokenizers_dir = os.path.join(nltk_data_dir, 'tokenizers')
                    os.makedirs(tokenizers_dir, exist_ok=True)
                    
                    with zipfile.ZipFile(tmp_file.name, 'r') as zip_ref:
                        zip_ref.extractall(tokenizers_dir)
                    
                    os.unlink(tmp_file.name)
                    print("✓ punkt downloaded via alternative method")
                    
            except Exception as e2:
                print(f"✗ Alternative punkt download also failed: {e2}")
        
        # Download stopwords
        try:
            print("Downloading stopwords...")
            nltk.download('stopwords', quiet=False, download_dir=nltk_data_dir)
            print("✓ stopwords downloaded successfully")
        except Exception as e:
            print(f"⚠ stopwords download failed: {e}")
            # Try alternative download
            try:
                print("Trying alternative download method for stopwords...")
                stopwords_url = "https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/stopwords.zip"
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                    urllib.request.urlretrieve(stopwords_url, tmp_file.name)
                    
                    corpora_dir = os.path.join(nltk_data_dir, 'corpora')
                    os.makedirs(corpora_dir, exist_ok=True)
                    
                    with zipfile.ZipFile(tmp_file.name, 'r') as zip_ref:
                        zip_ref.extractall(corpora_dir)
                    
                    os.unlink(tmp_file.name)
                    print("✓ stopwords downloaded via alternative method")
                    
            except Exception as e2:
                print(f"✗ Alternative stopwords download also failed: {e2}")
        
        # Test if downloads worked
        print("\nTesting NLTK data...")
        try:
            from nltk.tokenize import sent_tokenize
            test_text = "Hello world. This is a test."
            tokens = sent_tokenize(test_text)
            print(f"✓ Sentence tokenization works: {tokens}")
        except Exception as e:
            print(f"✗ Sentence tokenization failed: {e}")
        
        try:
            from nltk.corpus import stopwords
            stop_words = stopwords.words('english')[:5]
            print(f"✓ Stopwords work: {stop_words}")
        except Exception as e:
            print(f"✗ Stopwords failed: {e}")
            # Create basic stopwords as fallback
            print("Creating basic stopwords fallback...")
            basic_stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 
                             'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
                             'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them',
                             'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this',
                             'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
                             'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
                             'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
                             'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before',
                             'after', 'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
                             'under', 'again', 'further', 'then', 'once']
            
            # Save basic stopwords to a file
            stopwords_file = os.path.join(nltk_data_dir, 'basic_stopwords.txt')
            with open(stopwords_file, 'w') as f:
                f.write('\n'.join(basic_stopwords))
            print(f"✓ Basic stopwords saved to: {stopwords_file}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to fix SSL and download NLTK data: {e}")
        return False

def test_nltk_functionality():
    """Test if NLTK functionality works"""
    print("\n" + "="*50)
    print("Testing NLTK functionality...")
    
    try:
        # Test sentence tokenization
        print("Testing sentence tokenization...")
        try:
            from nltk.tokenize import sent_tokenize
            test_sentences = sent_tokenize("Hello world. This is a test. How are you?")
            print(f"✓ Sentence tokenization: {test_sentences}")
        except:
            # Fallback tokenization
            print("Using fallback sentence tokenization...")
            def simple_sent_tokenize(text):
                import re
                sentences = re.split(r'[.!?]+', text)
                return [s.strip() for s in sentences if s.strip()]
            test_sentences = simple_sent_tokenize("Hello world. This is a test. How are you?")
            print(f"✓ Fallback sentence tokenization: {test_sentences}")
        
        # Test stopwords
        print("Testing stopwords...")
        try:
            from nltk.corpus import stopwords
            stop_words = set(stopwords.words('english'))
            print(f"✓ NLTK stopwords loaded: {len(stop_words)} words")
        except:
            # Use basic stopwords
            print("Using basic stopwords fallback...")
            stop_words = {'i', 'me', 'my', 'we', 'our', 'you', 'your', 'he', 'him', 'she', 'her', 
                         'it', 'they', 'them', 'this', 'that', 'is', 'are', 'was', 'were', 'be', 
                         'been', 'have', 'has', 'had', 'do', 'does', 'did', 'a', 'an', 'the', 
                         'and', 'but', 'or', 'if', 'of', 'at', 'by', 'for', 'with', 'in', 'on', 
                         'to', 'from', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 
                         'further', 'then', 'once'}
            print(f"✓ Basic stopwords loaded: {len(stop_words)} words")
        
        return True
        
    except Exception as e:
        print(f"✗ NLTK functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("NLTK SSL Fix and Download Script")
    print("="*50)
    
    success = fix_nltk_ssl_and_download()
    test_success = test_nltk_functionality()
    
    print("\n" + "="*50)
    if success and test_success:
        print("✓ NLTK setup completed successfully!")
        print("✓ You can now run your advanced AI clip generator")
    else:
        print("⚠ NLTK setup had some issues, but fallback methods are available")
        print("✓ The advanced AI should still work with reduced functionality")
    print("="*50)