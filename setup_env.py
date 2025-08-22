#!/usr/bin/env python3
"""
Setup script for Talk2Trade environment variables
"""
import os
import getpass

def setup_environment():
    print("Talk2Trade Environment Setup")
    print("=" * 40)
    
    # Check if .env file exists
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"Found existing {env_file} file")
        overwrite = input("Do you want to overwrite it? (y/N): ").lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    # Get OpenAI API key
    print("\n1. OpenAI API Configuration")
    print("-" * 30)
    openai_key = getpass.getpass("Enter your OpenAI API key (input will be hidden): ")
    
    if not openai_key:
        print("Warning: No OpenAI API key provided. The AI features will not work.")
    
    # Get Kalshi API credentials
    print("\n2. Kalshi API Configuration")
    print("-" * 30)
    demo_keyid = input("Enter your Kalshi Demo Key ID: ")
    demo_keyfile = input("Enter path to your Kalshi Demo private key file: ")
    
    prod_keyid = input("Enter your Kalshi Production Key ID (optional): ")
    prod_keyfile = input("Enter path to your Kalshi Production private key file (optional): ")
    
    # Create .env content
    env_content = f"""# OpenAI API Configuration
OPENAI_API_KEY={openai_key}

# Kalshi API Configuration
DEMO_KEYID={demo_keyid}
DEMO_KEYFILE={demo_keyfile}
"""
    
    if prod_keyid and prod_keyfile:
        env_content += f"PROD_KEYID={prod_keyid}\nPROD_KEYFILE={prod_keyfile}\n"
    
    # Write .env file
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"\n✅ Environment file created successfully: {env_file}")
        print("\nNext steps:")
        print("1. Make sure your .env file is in your .gitignore")
        print("2. Restart your Flask application")
        print("3. Test the chat functionality")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        print("\nYou can manually create a .env file with the following content:")
        print(env_content)

if __name__ == "__main__":
    setup_environment()
