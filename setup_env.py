import os

def setup_api_key():
    print("Welcome to the Gemini API Key Setup!")
    print("\n1. Visit https://makersuite.google.com/app/apikey")
    print("2. Sign in with your Google account")
    print("3. Click 'Create API Key' to generate a new key")
    print("4. Copy the API key\n")
    
    api_key = input("Please enter your Gemini API key: ").strip()
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(f'GEMINI_API_KEY={api_key}')
    
    print("\nAPI key has been saved to .env file!")
    print("You can now run your Flask application.")

if __name__ == "__main__":
    setup_api_key() 