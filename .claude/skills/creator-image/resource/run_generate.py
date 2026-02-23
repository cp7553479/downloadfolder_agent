#!/usr/bin/env python3
"""
Run Generate Script
Calls the run endpoint to generate images based on a prompt and reference images.
"""
import sys
import os
import requests
import json
import time

# API Configuration
RUN_URL = "https://4h9jgmybb2.coze.site/run"
API_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjY0YjgyZWQ2LTJhYWMtNDQ2Mi1iNWNkLTU4OTVlN2QyMGY5OSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIlFiRU5pYVZVOUMwZEhHQWpZaHBkWUFWVTZDd1gwS1JjIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzY4OTg3NTQ2LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NTk3NDg4MTA3OTY0ODU4Mzg3Iiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NTk3NzQzNjU5OTU3NjE2NjY2In0.XRePGSJGH24B4er-VgYfbEfrYqtK9oeEjE7nemZjcBoVevxv753yrw78TUeFsElTUgh81rUnzFuQCHdwFmSHjXy7ri68KdEIYmLW-E-kYQTF0pUHNNIR_oOCVvK8cG2c8KxYWnH0iKH8CzgEIZHvxtubRAmyfwG44Q8rK95PGBINHlLtDnqA4OM5XTUCbnYCIf3Vcv6nNrbxnrU4hE_ougIKMQZ0bCoJFJTcBJ4WdteiVggMvu7s-2G5u2hcZChC5O2h1-VkWi6BiWY33i-JiclmgvIfe5Fb_7v-jGLoJdtr-2pRPfvSjhhEflitVlu8wtgnULcdAQmhj86_QEqheQ"

def run_generate_api(user_prompt, reference_images):
    """
    Call the run endpoint.
    
    Args:
        user_prompt: The prompt text.
        reference_images: List of dicts [{"url": "...", "file_type": "image"}]
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "user_prompt": user_prompt,
        "reference_images": reference_images
    }
    
    print("-" * 50)
    print("Calling Run Endpoint...")
    print(f"Prompt: {user_prompt}")
    print(f"Number of reference images: {len(reference_images)}")
    print("Waiting for response (timeout set to 600s)...")
    
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    session.mount('https://', adapter)
    
    try:
        response = session.post(RUN_URL, headers=headers, json=data, timeout=600)
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "=" * 50)
            print("SUCCESS! Result:")
            print("=" * 50)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
        else:
            print(f"\nAPI Error: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.Timeout:
        print("\nError: Request timed out after 600 seconds.")
        return None
    except Exception as e:
        print(f"\nError: {e}")
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 run_generate.py <user_prompt> <url1> [url2] ...")
        print("Example: python3 run_generate.py 'Laptop Stand' https://site.com/img1.jpg https://site.com/img2.jpg")
        sys.exit(1)
        
    user_prompt = sys.argv[1]
    urls = sys.argv[2:]
    
    if not urls:
         print("Error: No URLs provided.")
         sys.exit(1)
         
    reference_images = []
    for url in urls:
        reference_images.append({
            "url": url,
            "file_type": "image"
        })
            
    run_generate_api(user_prompt, reference_images)

if __name__ == "__main__":
    main()
