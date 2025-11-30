"""
Test client for Background Remover API
This script demonstrates how to use the API programmatically
"""

import requests
import sys
from pathlib import Path

# API Configuration
API_URL = "http://localhost:8000"


def test_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✓ API is healthy:", response.json())
            return True
        else:
            print("✗ API health check failed")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        return False


def remove_background_simple(image_path, output_path):
    """Simple background removal with default settings"""
    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{API_URL}/remove-background-simple", files=files)
        
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"✓ Background removed successfully: {output_path}")
            return True
        else:
            print(f"✗ Error: {response.json()}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def remove_background_advanced(image_path, output_path, **params):
    """Advanced background removal with custom parameters"""
    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{API_URL}/remove-background",
                files=files,
                params=params
            )
        
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"✓ Background removed successfully: {output_path}")
            return True
        else:
            print(f"✗ Error: {response.json()}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    print("=== Background Remover API Test Client ===\n")
    
    # Test 1: Health Check
    print("1. Testing API health...")
    if not test_health():
        print("\n⚠ Make sure the API server is running:")
        print("   python main.py")
        sys.exit(1)
    
    print("\n" + "="*50 + "\n")
    
    # Example usage (requires an actual image file)
    # Uncomment and modify the path to test with your own image
    
    # print("2. Testing simple background removal...")
    # remove_background_simple("test_image.jpg", "output_simple.png")
    
    # print("\n3. Testing with human segmentation model...")
    # remove_background_advanced(
    #     "portrait.jpg",
    #     "output_portrait.png",
    #     model="u2net_human_seg",
    #     alpha_matting=True
    # )
    
    # print("\n4. Testing with custom background color...")
    # remove_background_advanced(
    #     "test_image.jpg",
    #     "output_white_bg.png",
    #     background_color="255,255,255"
    # )
    
    # print("\n5. Testing mask generation...")
    # remove_background_advanced(
    #     "test_image.jpg",
    #     "output_mask.png",
    #     only_mask=True
    # )
    
    print("\nAPI is ready to use!")
    print("\nExample usage:")
    print('  remove_background_simple("your_image.jpg", "output.png")')


if __name__ == "__main__":
    main()
