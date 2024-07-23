import json
import requests
import os
import argparse
from tqdm import *

from concurrent.futures import ThreadPoolExecutor, as_completed


CURSEFORGE_API_BASE = "https://curseforge.com/api/v1"
SERVER_PACK_BASE = "output/"


def format_forge_download_uri(minecraft_ver,forge_ver):
    return f"https://maven.minecraftforge.net/net/minecraftforge/forge/{minecraft_ver}-{forge_ver}/forge-{minecraft_ver}-{forge_ver}-installer.jar'"

def download_file(mods_path,project_id, file_id):
    download_url = f"{CURSEFORGE_API_BASE}/mods/{project_id}/files/{file_id}/download"
    
    if not os.path.exists(mods_path):
        os.makedirs(mods_path)
    
    response = requests.get(download_url,allow_redirects = True)
    
    if response.status_code == 200:
        final_url = response.url;        
        filename = final_url.split("/")[-1]

        file_path = os.path.join(mods_path, filename)
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
    else:
        print(f"Failed to download file {download_url}: {response.status_code}")

def load_json_from_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def main():
    parser = argparse.ArgumentParser(description='Download files referenced in a JSON file.')
    parser.add_argument('json_file', type=str, help='Path to the JSON file')
    args = parser.parse_args()
    
    json_filename = args.json_file
    
    try:
        data = load_json_from_file(json_filename)
    except FileNotFoundError:
        print(f"File not found: {json_filename}")
        return
    except json.JSONDecodeError:
        print("Error decoding JSON file.")
        return
    
    files = data.get('files', [])
    

    # Use ThreadPoolExecutor to download files concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for file_info in files:
            project_id = file_info.get('projectID')
            file_id = file_info.get('fileID')
            if project_id and file_id:
                futures.append(executor.submit(download_file, "test", project_id, file_id))
            else:
                print(f"Invalid file information: {file_info}")

        for future in tqdm(as_completed(futures), total=len(futures), desc="Downloading mods..."):
            future.result()  # Wait for all futures to complete
if __name__ == "__main__":
    main()
