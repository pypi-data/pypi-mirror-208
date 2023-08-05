import requests

def get_upload_url(name, apiKey):
    url = f"https://peer-ai.com/gateway/upload_url?name={name}"
    headers = {
        "x-api-key": apiKey
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # print("Response Data:", data)
        # print("Response Headers:", response.headers)
    else:
        print("Error:", response.status_code, response.text)
        raise Exception("Error:", response.status_code, response.text)
    return data


def get_model_upload_url(name, apiKey):
    url = f"https://peer-ai.com/gateway/model_upload_url?name={name}"
    headers = {
        "x-api-key": apiKey
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("Response Data:", data)
        # print("Response Headers:", response.headers)        
    else:
        print("Error:", response.status_code, response.text)
        raise Exception("Error:", response.status_code, response.text)
    return data
