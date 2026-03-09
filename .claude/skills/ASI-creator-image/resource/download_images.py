#!/usr/bin/env python3
"""
Download Images Script
Downloads images from a list of URLs to a specified directory.
"""
import sys
import os
import warnings
# Suppress urllib3 OpenSSL warning
warnings.filterwarnings("ignore", category=UserWarning, module='urllib3')

import requests
import json
import time
from pathlib import Path

def download_image(url, output_dir, index):
    """
    Download a single image.
    """
    try:
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        session.mount('https://', adapter)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        response = session.get(url, stream=True, timeout=60, headers=headers)
        if response.status_code == 200:
            import mimetypes
            content_type = response.headers.get('content-type')
            ext = mimetypes.guess_extension(content_type) or '.png'
            
            # Generate filename based on timestamp and index
            timestamp = int(time.time() * 1000)
            filename = f"generated_{timestamp}_{index}{ext}"
            output_path = os.path.join(output_dir, filename)
            
            print(f"  Downloading: {url} -> {filename}")
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"  ✓ Saved to: {output_path}")
            return output_path
        else:
            print(f"  ✗ Failed to download: {response.status_code} - {url}")
            return None
    except Exception as e:
        print(f"  ✗ Error downloading: {e}")
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 download_images.py <output_dir> <url1> [url2] ...")
        sys.exit(1)
        
    output_dir = sys.argv[1]
    
    # Create directory if it doesn't exist
    if not os.path.exists(output_dir):
        print(f"Creating directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        
    # Assume remaining arguments are URLs
    urls = sys.argv[2:]
        
    if not urls:
        print("No URLs to download.")
        sys.exit(0)
        
    print(f"Starting download of {len(urls)} images to {output_dir}...")
    
    downloaded_count = 0
    for i, url in enumerate(urls):
        result = download_image(url, output_dir, i)
        if result:
            downloaded_count += 1
            
    print("\n" + "=" * 50)
    print(f"Download Complete: {downloaded_count}/{len(urls)} successful")
    print("=" * 50)

if __name__ == "__main__":
    main()
