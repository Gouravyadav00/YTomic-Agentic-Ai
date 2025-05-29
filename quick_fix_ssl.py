# quick_fix_ssl.py
# Quick fix for NLTK SSL issues

print("Fixing NLTK SSL certificate issues...")

try:
    # Fix SSL certificates
    import ssl
    import certifi
    import os
    
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
    
    # Disable SSL verification for NLTK downloads (less secure but works)
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    print("✓ SSL certificates configured")
    
    # Now try to download NLTK data
    import nltk
    
    print("Downloading NLTK data...")
    try:
        nltk.download('punkt', quiet=True)
        print("✓ punkt downloaded")
    except:
        print("⚠ punkt download failed - using fallback")
    
    try:
        nltk.download('stopwords', quiet=True)
        print("✓ stopwords downloaded")
    except:
        print("⚠ stopwords download failed - using fallback")
    
    print("✓ NLTK setup completed (with fallbacks if needed)")
    
except Exception as e:
    print(f"⚠ SSL fix failed: {e}")
    print("The advanced AI will use fallback methods")

print("\nYou can now run your Flask app!")