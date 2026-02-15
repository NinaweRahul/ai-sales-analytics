"""
Setup Script - Initialize the AI Sales Analytics System
"""
import os
import sys

def create_directories():
    """Create necessary project directories"""
    directories = [
        'data',
        'src',
        'outputs',
        'sql_queries',
        'tableau_exports'
    ]
    
    print("Creating project directories...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✓ {directory}/")
    print()

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print(".env file not found!")
        print("   Creating from template...")
        
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("   ✓ .env file created from .env.example")
            print()
            print("   IMPORTANT: Edit .env file with your credentials!")
            print("   You need to add:")
            print("   1. PostgreSQL password")
            print("   2. Gemini API key (get from https://makersuite.google.com/app/apikey)")
            print()
            return False
        else:
            print("   .env.example not found. Please create .env manually.")
            print()
            print("   Your .env should contain:")
            print("   DB_HOST=localhost")
            print("   DB_PORT=5432")
            print("   DB_NAME=sales_analytics")
            print("   DB_USER=postgres")
            print("   DB_PASSWORD=your_password")
            print("   GEMINI_API_KEY=your_gemini_api_key")
            print()
            return False
    else:
        print("✓ .env file exists")
        print()
        return True

def check_dependencies():
    """Check if required packages are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        ('pandas', 'pandas'),
        ('psycopg2', 'psycopg2'),
        ('sqlalchemy', 'sqlalchemy'),
        ('google.genai', 'google-genai'),
        ('dotenv', 'python-dotenv'),
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'seaborn'),
        ('openpyxl', 'openpyxl'),
        ('tabulate', 'tabulate')
    ]
    
    missing = []
        
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name}")
            missing.append(package_name)
    
    print()
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        print()
        return False
    else:
        print("✓ All dependencies installed")
        print()
        return True

def test_database_connection():
    """Test database connection"""
    print("🔌 Testing database connection...")
    
    try:
        # Change to src directory to import config
        sys.path.insert(0, 'src')
        from config import test_connection
        
        if test_connection():
            print("✓ Database connection successful")
            print()
            return True
        else:
            print("✗ Database connection failed")
            print("  Please check:")
            print("  1. PostgreSQL is running")
            print("  2. Database 'sales_analytics' exists")
            print("  3. Credentials in .env are correct")
            print()
            return False
    except Exception as e:
        print(f"✗ Error testing connection: {e}")
        print("  Make sure PostgreSQL is installed and running")
        print()
        return False

def test_gemini_api_key():
    """Test Gemini API key"""
    print("Testing Gemini API key...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('GEMINI_API_KEY', '')
        
        if not api_key or api_key == 'your_gemini_api_key_here':
            print("✗ Gemini API key not configured")
            print("  Please add your Gemini API key to .env file")
            print("  Get one FREE at: https://makersuite.google.com/app/apikey")
            print()
            return False
        
        # Check if key starts with expected format
        if not api_key.startswith('AIza'):
            print("Warning: API key doesn't start with 'AIza'")
            print("  Gemini API keys typically start with 'AIza'")
            print("  Please verify your key is correct")
            print()
        
        # Test the API key
        from google import genai
        client = genai.Client(api_key=api_key)
        
        # Test with a simple message
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents="Say 'Hello'"
        )
        
        if response and response.text:
            print("✓ Gemini API key valid and working")
            print(f"  Response: {response.text[:50]}...")
            print(f"  Model: gemini-2.0-flash-exp")
            print()
            return True
        else:
            print("✗ Gemini API returned empty response")
            print()
            return False
        
    except ImportError:
        print("✗ google-genai package not installed")
        print("  Run: pip install google-genai")
        print()
        return False
    
    except Exception as e:
        error_msg = str(e).lower()
        
        if 'api key not valid' in error_msg or 'invalid' in error_msg:
            print("✗ Invalid API key")
            print("  Please check your Gemini API key in .env file")
            print("  Get a new one at: https://makersuite.google.com/app/apikey")
        elif '429' in str(e) or 'resource_exhausted' in error_msg or 'quota' in error_msg:
            print("  API quota/rate limit hit")
            print("  But your API key seems valid!")
            return True  # Key is valid, just hit rate limit
        else:
            print(f"✗ Gemini API test failed: {e}")
            print("  Please verify:")
            print("  1. API key is correct in .env")
            print("  2. You have internet connection")
            print("  3. Google AI services are accessible")
        print()
        return False

def check_data_file():
    """Check if data file exists"""
    print("Checking for data file...")
    
    data_file = 'data/sales_data.csv'
    
    if os.path.exists(data_file):
        print(f"✓ Found: {data_file}")
        
        # Get file size
        size_mb = os.path.getsize(data_file) / (1024 * 1024)
        print(f"  Size: {size_mb:.2f} MB")
        
        # Try to count lines
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
            print(f"  Lines: {line_count:,}")
        except Exception:
            pass
        
        print()
        return True
    else:
        print(f"✗ Data file not found: {data_file}")
        print("  Please place your sales_data.csv file in the data/ directory")
        print()
        return False

def check_gitignore():
    """Check if .gitignore properly protects .env"""
    print("Checking .gitignore security...")
    
    if not os.path.exists('.gitignore'):
        print(".gitignore file not found!")
        print("  This is a security risk - your API key could be exposed!")
        print("  Please add a .gitignore file")
        print()
        return False
    
    with open('.gitignore', 'r') as f:
        content = f.read()
    
    if '.env' in content:
        print("✓ .gitignore protects .env file")
        print()
        return True
    else:
        print("WARNING: .env not in .gitignore!")
        print("  Your API key could be exposed to GitHub!")
        print("  Add '.env' to your .gitignore file immediately")
        print()
        return False

def main():
    """Main setup function"""
    print("\n" + "=" * 80)
    print("AI SALES ANALYTICS SYSTEM - SETUP (Gemini Edition)")
    print("=" * 80)
    print()
    
    # Create directories
    create_directories()
    
    # Check environment file
    env_ok = check_env_file()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check data file
    data_ok = check_data_file()
    
    # Check .gitignore
    gitignore_ok = check_gitignore()
    
    if not deps_ok:
        print("Setup incomplete: Missing dependencies")
        print()
        print("   Quick fix:")
        print("   1. Make sure virtual environment is activated")
        print("   2. Run: python -m pip install --upgrade pip")
        print("   3. Run: pip install -r requirements.txt")
        print()
        return
    
    if not env_ok:
        print("Setup incomplete: Configure .env file")
        print()
        print("   Steps:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your PostgreSQL password")
        print("   3. Get FREE Gemini API key: https://makersuite.google.com/app/apikey")
        print("   4. Add Gemini API key to .env")
        print()
        return
    
    # Test database
    db_ok = test_database_connection()
    
    # Test Gemini API key
    api_ok = test_gemini_api_key()
    
    # Summary
    print("=" * 80)
    print("SETUP SUMMARY")
    print("=" * 80)
    print(f"Directories:  {'✓' if True else '✗'}")
    print(f"Dependencies: {'✓' if deps_ok else '✗'}")
    print(f"Environment:  {'✓' if env_ok else '✗'}")
    print(f"Database:     {'✓' if db_ok else '✗'}")
    print(f"Gemini API:   {'✓' if api_ok else '✗'}")
    print(f"Data File:    {'✓' if data_ok else '✗'}")
    print(f".gitignore:   {'✓' if gitignore_ok else '✗'}")
    print()
    
    if all([deps_ok, env_ok, db_ok, api_ok, data_ok, gitignore_ok]):
        print("Setup complete! You're ready to go!")
    else:
        print("Setup incomplete. Please resolve the issues above.")
        print()
        print("Setup checklist:")
        if not deps_ok:
            print("  □ Install dependencies: pip install -r requirements.txt")
        if not env_ok:
            print("  □ Configure .env file with your credentials")
        if not db_ok:
            print("  □ Ensure PostgreSQL is running and credentials are correct")
            print("    - Check if PostgreSQL service is running")
            print("    - Verify database 'sales_analytics' exists")
        if not api_ok:
            print("  □ Add valid Gemini API key to .env")
            print("    - Get FREE key: https://makersuite.google.com/app/apikey")
            print("    - No credit card required!")
        if not data_ok:
            print("  □ Place sales_data.csv in data/ directory")
        if not gitignore_ok:
            print("  □ Add .env to .gitignore for security")
        print()

if __name__ == "__main__":
    main()
