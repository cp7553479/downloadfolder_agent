import os
import sys
import json
import urllib.request
import urllib.error
import argparse

def generate_image(
    prompt,
    model=None,
    api_key=None,
    size=None,
    watermark=None,
    optimize_prompt_options=None,
    tools=None,
    output_format=None,
    sequential_image_generation=None,
    download_dir=None
):
    """
    Generates an image using the Volcengine Seedream API.
    
    Args:
        prompt (str): The text description of the image to generate. Required.
        model (str): The target model endpoint ID (e.g., ep-xxxx). Required.
        api_key (str, optional): Custom API key to access Volcengine Ark. Defaults to None.
        size (str, optional): Target image size. Can be a resolution class (e.g., '2K', '3K') 
                              or explicit dimensions (e.g., '2048x2048'). Defaults to None.
        watermark (bool, optional): Whether to add an AI watermark. Defaults to False.
        optimize_prompt_options (dict, optional): Options to optimize the prompt (e.g., {"mode": "standard"}). Defaults to None.
        tools (list, optional): A list of tools for the model to use (e.g., [{"type": "web_search"}]).
        output_format (str, optional): Output image format (e.g., 'png', 'jpeg', 'webp'). Defaults to None.
        sequential_image_generation (str, optional): Sequential image generation strategy (e.g., 'auto'). Defaults to None.

    Environment Variable Reading Logic:
        1. Checks if `api_key` param was explicitly provided to the function.
        2. If missing, attempts to read from the OS environment variable `ARK_API_KEY`.
        3. If still missing, sequentially checks for a `.env` file containing `ARK_API_KEY=` 
           in three locations: `/.env`, `./.env` (current directory), and `<script_directory>/.env`.
        4. If the key is not found after all attempts, returns a dictionary with an error message prompting setup.
        
    Returns:
        dict: The JSON response dictionary.
        
        Successful Return Value Format:
        {
          "data": [
            {
              "url": "https://...",
              "size": "2048x2048" # Included depending on the model capability
            }
          ],
          "usage": { 
              "generated_images": 1,
              ...
          }
        }
        
        Failure Return Value Format:
        {
          "error": "<Error Code or Details>",
          "message": "<Optional detailed message from server>"
        }
    """
    # Retrieve API key
    key_read_from_arg = api_key is not None
    key = api_key or os.environ.get("ARK_API_KEY")
    if not key:
        for path in ["/.env", ".env", sys.path[0] + "/.env"]:
            if os.path.exists(path):
                with open(path, "r") as f:
                    for line in f:
                        if line.startswith("ARK_API_KEY="):
                            key = line.strip().split("=", 1)[1].strip().strip("\"'")
                            break
            if key:
                break
    
    model_id = model or os.environ.get("SEEDREAM_ENDPOINT_ID")
    if not model_id and not key_read_from_arg:
        for path in ["/.env", ".env", sys.path[0] + "/.env"]:
            if os.path.exists(path):
                with open(path, "r") as f:
                    for line in f:
                        if line.startswith("SEEDREAM_ENDPOINT_ID="):
                            model_id = line.strip().split("=", 1)[1].strip().strip("\"'")
                            break
            if model_id:
                break

    if not model_id:
        return {"error": "Require model or SEEDREAM_ENDPOINT_ID in .env/environment"}

    url = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
    payload = {
        "model": model_id,
        "prompt": prompt,
        "watermark": watermark if watermark is not None else False
    }
    
    if size is not None:
        payload["size"] = size
    if optimize_prompt_options is not None:
        payload["optimize_prompt_options"] = optimize_prompt_options
    if tools is not None:
        payload["tools"] = tools
    if output_format is not None:
        payload["output_format"] = output_format
    if sequential_image_generation is not None:
        payload["sequential_image_generation"] = sequential_image_generation

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            
            # If successful, handle downloads if download_dir is provided
            if "data" in res_json:
                res_json["input_params"] = payload
                
                if download_dir:
                    save_path = download_dir
                    if not os.path.exists(save_path):
                        os.makedirs(save_path)
                    
                    for item in res_json["data"]:
                        if "url" in item:
                            try:
                                file_ext = ".png" if payload.get("output_format") == "png" else ".jpeg"
                                filename = f"image_{int(res_json.get('created', 0))}_{res_json['data'].index(item)}{file_ext}"
                                local_file_path = os.path.join(save_path, filename)
                                
                                urllib.request.urlretrieve(item["url"], local_file_path)
                                item["local_path"] = local_file_path
                            except Exception as download_err:
                                item["local_path_error"] = str(download_err)
            
            return res_json
    except urllib.error.HTTPError as e:
        return {"error": e.code, "message": e.read().decode("utf-8")}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seedream Image Generation API Wrapper")
    parser.add_argument("--prompt", type=str, required=True, help="Image generation prompt")
    parser.add_argument("--model", type=str, help="Model endpoint id (if not provided, reads SEEDREAM_ENDPOINT_ID)")
    parser.add_argument("--api_key", type=str, help="Volcengine Ark API Key")
    parser.add_argument("--size", type=str, help="Image size")
    parser.add_argument("--watermark", type=str, help="Add watermark (true/false)")
    parser.add_argument("--optimize_prompt_options", type=str, help="JSON string for prompt optimization options")
    parser.add_argument("--tools", type=str, help="JSON string for tools list, e.g. '[{\"type\": \"web_search\"}]'")
    parser.add_argument("--output_format", type=str, help="Output image format (png, jpeg)")
    parser.add_argument("--sequential_image_generation", type=str, help="Sequential image generation mode (e.g., 'auto')")
    parser.add_argument("--download_dir", type=str, help="Directory to save images")
    args = parser.parse_args()
    
    watermark_val = None
    if args.watermark is not None:
        watermark_val = args.watermark.lower() == "true"
        
    optimize_prompt_val = None
    if args.optimize_prompt_options is not None:
        try:
            optimize_prompt_val = json.loads(args.optimize_prompt_options)
        except json.JSONDecodeError:
            print("Error: --optimize_prompt_options must be a valid JSON string.")
            sys.exit(1)

    tools_val = None
    if args.tools is not None:
        try:
            tools_val = json.loads(args.tools)
        except json.JSONDecodeError:
            print("Error: --tools must be a valid JSON string.")
            sys.exit(1)

    res = generate_image(
        prompt=args.prompt,
        model=args.model,
        api_key=args.api_key,
        size=args.size,
        watermark=watermark_val,
        optimize_prompt_options=optimize_prompt_val,
        tools=tools_val,
        output_format=args.output_format,
        sequential_image_generation=args.sequential_image_generation,
        download_dir=args.download_dir
    )
    print(json.dumps(res, indent=2))
