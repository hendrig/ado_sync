import os
import fnmatch
import json
import base64
import sys
from parse_and_send import convert_and_send

def load_sync_config(file_path="ado_config.json"):	
    """	
    Load synchronization configuration from a JSON file.	
    Args:	
        file_path (str, optional): The path to the synchronization configuration JSON file.	
            Defaults to "ado_config.json".	
    Returns:	
        dict: A dictionary containing synchronization configuration.	
    """	
    print("Loading configuration")	
    with open(file_path, "r", encoding="utf-8") as config_file:	
        sync_config = json.load(config_file)	
    return sync_config	

def find_feature_files(folder):
    """
    Find all .feature files in the given folder and its subfolders.

    Args:
    - folder: Path to the folder to search in.

    Returns:
    - List of paths to .feature files.
    """
    feature_files = []
    # Get the absolute path of the current script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Combine the script directory with the provided folder name
    folder_path = os.path.join(script_dir, folder)
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if fnmatch.fnmatch(file, '*.feature'):
                feature_files.append(os.path.join(root, file))
    return feature_files    

config_data = load_sync_config()	
folder_path = config_data["paths"]["features"]
credentials = config_data["credentials"]
personal_access_token = credentials["personal_access_token"]	
organization = credentials["organization_name"]	
project = credentials["project_name"]
url = f"https://dev.azure.com/{organization}/{project}/_apis/"

if len(personal_access_token) == 0:
    if len(sys.argv) != 2:
        print("Usage: python sync_folder.py <new_value>")
        sys.exit(1)
    personal_access_token = sys.argv[1]

headers = {
    "Content-Type": "application/json-patch+json; charset=utf-8",
    "Authorization": "Basic "
    + base64.b64encode(f"{personal_access_token}:".encode()).decode(),	
}

if __name__ == "__main__":
    feature_files = find_feature_files(folder_path)
    for file_path in feature_files:
        print(f"\nSyncing file {file_path}")
        convert_and_send(file_path, headers, organization, project)