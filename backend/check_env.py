"""
Check .env file and API keys configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

print("=" * 60)
print("Environment Variables Check")
print("=" * 60)

# Find .env file
env_path = Path(".env")
if not env_path.exists():
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        env_path = Path(__file__).parent.parent.parent / ".env"

if env_path.exists():
    print(f"\n✅ Found .env file: {env_path.absolute()}")
    load_dotenv(env_path)
else:
    print(f"\n❌ .env file not found!")
    print(f"   Looked in: {Path.cwd()}, {Path(__file__).parent.parent}")
    print(f"\n   Please create .env file by copying env_template.txt:")
    print(f"   cp env_template.txt .env")
    print(f"   Then edit .env and add your API keys")
    exit(1)

print("\n" + "=" * 60)
print("API Keys Status")
print("=" * 60)

# Check each API key
api_keys = {
    "MINIMAX_API_KEY": {
        "required": True,
        "description": "Required for Minimax text-to-video",
        "get_url": "https://modelstudio.console.alibabacloud.com/?tab=dashboard#/api-key"
    }
}

all_ok = True
for key_name, info in api_keys.items():
    value = os.getenv(key_name, "")
    
    if not value:
        status = "❌ MISSING"
        all_ok = False if info["required"] else all_ok
    elif value.startswith("your_") or value == "":
        status = "⚠️  PLACEHOLDER"
        all_ok = False if info["required"] else all_ok
    elif len(value) < 10:
        status = "⚠️  INVALID (too short)"
        all_ok = False if info["required"] else all_ok
    else:
        status = "✅ OK"
        value_display = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else f"{value[:10]}..."
    
    required_mark = " [REQUIRED]" if info["required"] else " [OPTIONAL]"
    print(f"\n{key_name}{required_mark}:")
    print(f"  Status: {status}")
    if status == "✅ OK":
        print(f"  Value: {value_display} (length: {len(value)})")
    print(f"  Description: {info['description']}")
    print(f"  Get it from: {info['get_url']}")

print("\n" + "=" * 60)
if all_ok:
    print("✅ All required API keys are configured!")
else:
    print("⚠️  Some API keys are missing or invalid")
    print("\nTo fix:")
    print("1. Edit .env file")
    print("2. Replace placeholder values with actual API keys")
    print("3. Restart the backend server")
print("=" * 60)

