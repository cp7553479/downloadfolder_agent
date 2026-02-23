#!/usr/bin/env python3
"""
文件上传脚本
使用upload端点上传文件到对象存储并返回URL
"""
import sys
import os
import requests
import json
import time
from pathlib import Path

# API配置
UPLOAD_URL = "https://4h9jgmybb2.coze.site/upload"
API_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjY0YjgyZWQ2LTJhYWMtNDQ2Mi1iNWNkLTU4OTVlN2QyMGY5OSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIlFiRU5pYVZVOUMwZEhHQWpZaHBkWUFWVTZDd1gwS1JjIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzY4OTg3NTQ2LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NTk3NDg4MTA3OTY0ODU4Mzg3Iiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NTk3NzQzNjU5OTU3NjE2NjY2In0.XRePGSJGH24B4er-VgYfbEfrYqtK9oeEjE7nemZjcBoVevxv753yrw78TUeFsElTUgh81rUnzFuQCHdwFmSHjXy7ri68KdEIYmLW-E-kYQTF0pUHNNIR_oOCVvK8cG2c8KxYWnH0iKH8CzgEIZHvxtubRAmyfwG44Q8rK95PGBINHlLtDnqA4OM5XTUCbnYCIf3Vcv6nNrbxnrU4hE_ougIKMQZ0bCoJFJTcBJ4WdteiVggMvu7s-2G5u2hcZChC5O2h1-VkWi6BiWY33i-JiclmgvIfe5Fb_7v-jGLoJdtr-2pRPfvSjhhEflitVlu8wtgnULcdAQmhj86_QEqheQ"


def upload_file(file_path):
    """
    上传单个文件到对象存储
    
    参数:
        file_path: 要上传的文件路径
    
    返回:
        {
            "file_key": "对象存储中的文件key",
            "file_url": "可访问的文件URL",
            "filename": "原始文件名",
            "content_type": "文件MIME类型",
            "size": "文件大小(字节)"
        }
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    # 准备请求头
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    # 准备文件 - 清理文件名以符合S3命名规范
    original_name = os.path.basename(file_path)
    # 获取文件扩展名
    name_parts = os.path.splitext(original_name)
    ext = name_parts[1] if len(name_parts) > 1 else ''
    
    # 生成安全的文件名（使用timestamp + 扩展名）
    import time
    # 使用纳秒确保文件名唯一，避免快速上传时重复
    safe_name = f"upload_{time.time_ns()}{ext}"
    
    print(f"  上传: {original_name} -> {safe_name}")
    
    with open(file_path, 'rb') as f:
        files = {
            'file': (safe_name, f, 'image/jpeg')
        }
        
        # 使用 Session 和重试机制
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        session.mount('https://', adapter)
        
        # 发送请求，超时时间设置为120秒
        response = session.post(UPLOAD_URL, headers=headers, files=files, timeout=120)
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            # print(f"✓ 上传成功: {result.get('filename')}")
            # print(f"  文件URL: {result.get('file_url')}")
            return result
        else:
            print(f"✗ 上传失败: {response.status_code}")
            print(f"  响应: {response.text}")
            response.raise_for_status()


def process_path(path):
    """处理路径（文件或目录）并返回引用图像列表"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    files_to_upload = []
    
    path_obj = Path(path)
    if path_obj.is_file():
        files_to_upload.append(path_obj)
    elif path_obj.is_dir():
        for item in path_obj.iterdir():
            if item.is_file() and item.suffix.lower() in image_extensions:
                files_to_upload.append(item)
    else:
        print(f"错误: 路径不存在 {path}")
        return []

    print(f"找到 {len(files_to_upload)} 个图片文件待上传...")
    
    reference_images = []
    for file_path in sorted(files_to_upload):
        try:
            result = upload_file(str(file_path))
            file_url = result.get('file_url')
            if file_url:
                reference_images.append({
                    "url": file_url,
                    "file_type": "image"
                })
                print(f"  ✓ 成功获取URL: {file_url}")
        except Exception as e:
            print(f"  ✗ 处理失败 {file_path}: {e}")
            
    return reference_images

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 upload_file.py <文件或目录路径>")
        sys.exit(1)
    
    start_time = time.time()
    all_reference_images = []
    
    for path in sys.argv[1:]:
        refs = process_path(path)
        all_reference_images.extend(refs)
    
    print("\n" + "="*50)
    print("上传完成! 请复制以下JSON用于run脚本:")
    print("="*50)
    
    import json
    print(json.dumps(all_reference_images, indent=2, ensure_ascii=False))
    
    print(f"\n总用时: {time.time() - start_time:.2f} 秒")


if __name__ == "__main__":
    main()
