import json
import hashlib
import os
from urllib.parse import urlparse
import requests

def sha1(file_path):
    sha1 = hashlib.sha1()
    try:
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()
    except Exception as e:
        print(f"Error while hashing {file_path}: {e}")
        return ""

def download_file(url, local_filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Error while downloading {url}: {e}")
        return False

def get_filename_from_url(url):
    parsed = urlparse(url)
    return os.path.basename(parsed.path)

def process_mods_json(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    temp_dir = "temp_mods"
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"Processing required mods ({len(data['required'])}):")
    for mod in data['required']:
        url = mod['url']
        if url:
            filename = get_filename_from_url(url)
            local_path = os.path.join(temp_dir, filename)
            
            print(f"Downloading {filename}...")
            if download_file(url, local_path):
                sha1_hash = sha1(local_path)
                mod['sha1'] = sha1_hash
                print(f"  SHA1: {sha1_hash}")
            else:
                print(f"  ! Failed to download")
    
    print(f"\nProcessing optional mods ({len(data['optional'])}):")
    for mod in data['optional']:
        url = mod['url']
        if url:
            filename = get_filename_from_url(url)
            local_path = os.path.join(temp_dir, filename)
            
            print(f"Скачивание {filename}...")
            if download_file(url, local_path):
                sha1_hash = sha1(local_path)
                mod['sha1'] = sha1_hash
                print(f"  SHA1: {sha1_hash}")
            else:
                print(f"  Failed to download")
    
    output_file = "mods.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    import shutil
    shutil.rmtree(temp_dir)
    
    print(f"\nFile ready: {output_file}")
    return data


if __name__ == "__main__":
    process_mods_json("mods.json")
