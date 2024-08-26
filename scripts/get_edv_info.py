# require access to Domino and Kubernetes cluster
# Kubernetes configs can be read from ~/.kube/config
# pip install requests kubernetes
# set the export DOMINO_USER_API_KEY="domino api key"

import requests
import json
import os
from kubernetes import client, config

# Read the API key from the environment variable
api_key = os.getenv('DOMINO_USER_API_KEY')

# Define the headers
headers = {
    "accept": "application/json",
    "X-Domino-Api-Key": api_key
}

# Define the Domino API endpoint
domino_url = "https://prod-field.cs.domino.tech/v4/datamount/all"

# Function to get PV details from Kubernetes
def get_pv_details(pvc_name):
    v1 = client.CoreV1Api()
    pv_list = v1.list_persistent_volume()
    for pv in pv_list.items:
        if pv.spec.claim_ref and pv.spec.claim_ref.name == pvc_name:
            return {
                'pv_name': pv.metadata.name,
                'pv_size': pv.spec.capacity['storage']
            }
    return None

# Function to get data from Domino API
def get_domino_data():
    response = requests.get(domino_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get data: {response.status_code}")
        print(response.text)
        return None

# Main function
def main():
    # Load Kubernetes configuration
    config.load_kube_config()

    # Get data from Domino API
    data = get_domino_data()
    if not data:
        return

    # Process each item in the data
    for item in data:
        pvc_name = item.get('pvcName')
        project_info = item.get('projectsInfo', [])
        if pvc_name:
            pv_details = get_pv_details(pvc_name)
            if pv_details:
                print(f"PVC Name: {pvc_name}")
                print(f"  PV Name: {pv_details['pv_name']}")
                print(f"  PV Size: {pv_details['pv_size']}")
                for project in project_info:
                    print(f"  Project Name: {project['projectName']}")
                    print(f"  Project Owner Username: {project['projectOwnerUsername']}")
            else:
                print(f"PVC Name: {pvc_name} - No corresponding PV found")
                for project in project_info:
                    print(f"  Project Name: {project['projectName']}")
                    print(f"  Project Owner Username: {project['projectOwnerUsername']}")

if __name__ == "__main__":
    main()
