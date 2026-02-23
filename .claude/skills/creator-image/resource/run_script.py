#!/usr/bin/env python3
"""
Run Script
Combines upload, generate, and download steps into a single workflow.
"""
import sys
import os
import time
import json

# Add current directory to sys.path to allow importing sibling modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

import upload_file
import run_generate
import download_images

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_script.py <folder_path> [optional_prompt]")
        sys.exit(1)
        
    folder_path = sys.argv[1]
    if not os.path.isdir(folder_path):
        print(f"Error: Directory not found: {folder_path}")
        sys.exit(1)
        
    # Get absolute path
    folder_path = os.path.abspath(folder_path)
    folder_name = os.path.basename(folder_path)
    
    # Determine prompt: use argument if provided, otherwise default to folder name
    prompt = folder_name
    if len(sys.argv) > 2 and sys.argv[2].strip():
        prompt = sys.argv[2]
    
    print("=" * 60)
    print(f"Starting Workflow for Folder: {folder_name}")
    print(f"Target Prompt: '{prompt}'")
    print("=" * 60)
    
    # --- Step 1: Upload ---
    print("\n>>> Step 1: Uploading Images...")
    # upload_file.process_path returns a list of dicts: [{"url": "...", "file_type": "image"}, ...]
    reference_images = upload_file.process_path(folder_path)
    
    if not reference_images:
        print("No valid images found to upload. Exiting.")
        sys.exit(1)
        
    print(f"Uploaded {len(reference_images)} images.")
    
    # --- Step 2: Generate ---
    print(f"\n>>> Step 2: Generating Images (Prompt: '{prompt}')...")
    # run_generate_api returns a dict (the API response)
    # It expects reference_images as a list of dicts with "url" and "file_type"
    result = run_generate.run_generate_api(prompt, reference_images)
    
    if not result:
        print("Generation failed. Exiting.")
        sys.exit(1)
        
    # Extract URLs from result
    generated_urls = []
    # Try different keys that might contain the URLs
    if isinstance(result, list):
         # If it returns a list directly (unlikely based on previous code, but possible)
         generated_urls = [u['url'] if isinstance(u, dict) and 'url' in u else u for u in result]
    elif isinstance(result, dict):
        if 'data' in result and isinstance(result['data'], list):
             # Some coze endpoints return data wrappers
             # Adjust based on actua API response structure if known.
             # Based on previous code in download_images.py, we look for keys:
             pass
             
        keys_to_check = ['final_image_urls', 'image_urls', 'urls']
        for key in keys_to_check:
            if key in result and result[key]:
                generated_urls = result[key]
                break
                
    if not generated_urls:
        # Fallback dump to see what happened
        print("Warning: Could not identify image URLs in response.")
        print("Response structure:", json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)
        
    print(f"Generated {len(generated_urls)} image URLs.")
    
    # --- Step 3: Download ---
    print("\n>>> Step 3: Downloading Images...")
    download_count = 0
    for i, url in enumerate(generated_urls):
        saved_path = download_images.download_image(url, folder_path, i)
        if saved_path:
            download_count += 1
            
    print("\n" + "=" * 60)
    print(f"Workflow Complete! {download_count}/{len(generated_urls)} images saved to: {folder_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
