import requests
from tqdm import tqdm
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from pathlib import Path

def upload_google_cloud(file_path, info):
    # Set the URL to upload the file
    upload_url = info['url']
    fields = info['fields']

    # with open(file_path, "rb") as file:
    #     file_content = file.read()
    
    headers = {}
    
    # Get the total file size in bytes
    path = Path(file_path)
    # total_size = len(file_content)
    total_size = path.stat().st_size
    # filename = path.name

    # Create a progress bar using tqdm
    with tqdm(total=total_size, unit="B", unit_scale=True, desc=file_path) as progress:
        # Create the multipart form data request
        with open(file_path, "rb") as file:
            fields["file"] = ('filename', file, 'application/protobuf')
            e = MultipartEncoder(fields=fields)
            m = MultipartEncoderMonitor(
                e, lambda monitor: progress.update(monitor.bytes_read - progress.n)
            )
            headers = {"Content-Type": m.content_type}
            response = requests.post(upload_url, headers=headers, data=m)

        # Stream the file content to the server and update the progress bar
        # for chunk in response.iter_content(chunk_size=4096):
        #     print('chunk', chunk)
        #     progress.update(len(chunk))

    # Check the status code of the response
    if response.status_code >= 200 and response.status_code < 300:
        # print("File uploaded successfully.")
        pass
    else:
        print(f"Error uploading file: {response.text}")
        raise Exception(f"Error uploading file: {response.text}")
        
    modelURL = info['url'].replace('storage.googleapis.com/','') + info['fields']['key']
    return modelURL,total_size