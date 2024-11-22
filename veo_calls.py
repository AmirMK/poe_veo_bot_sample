import requests
import time
import google.auth
from google.oauth2 import service_account
import google.auth.transport.requests
from google.auth.transport.requests import Request
import base64


def send_request_to_google_api(api_endpoint, data=None):
    """
    Sends an HTTP request to a Google API endpoint.

    Args:
        api_endpoint: The URL of the Google API endpoint.
        data: (Optional) Dictionary of data to send in the request body (for POST, PUT, etc.).

    Returns:
        The response from the Google API.
    """

    
    # Get access token calling API inside GCP
    creds, project = google.auth.default()

    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    access_token = creds.token

    #  Get access token calling API outside of GCP
    """
    json_keyfile = "xxx.json"
    credentials = service_account.Credentials.from_service_account_file(
        json_keyfile,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    auth_req = Request()
    credentials.refresh(auth_req)
    access_token = credentials.token
    
    """
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }


    response = requests.post(api_endpoint, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def compose_videogen_request(prompt, image, seed, aspect_ratio, sample_count, length):
    instance = {"prompt": prompt}
    if image:    
        instance["image"] = {"bytesBase64Encoded": base64.b64encode(image['image_binary']).decode(), "mimeType": image['mimeType']}
    
    request = {
          "instances": [instance],
          "parameters": {"sampleCount": sample_count, "seed": seed, "aspectRatio": aspect_ratio, "durationSeconds": length}
      }
    
    return request

def fetch_operation(_FETCH_API_ENDPOINT,lro_name):
    request = {
     'operationName': lro_name}
  # The generation usually takes 2 minutes. Loop 30 times, around 5 minutes.
    for i in range(30):
        resp = send_request_to_google_api(_FETCH_API_ENDPOINT, request)        
        if 'done' in resp and resp['done']:
            return resp
        time.sleep(10)

def text_to_video(_PREDICT_API_ENDPOINT,_FETCH_API_ENDPOINT,prompt, seed, aspect_ratio, sample_count, length):          
    req = compose_videogen_request(prompt, None, seed, aspect_ratio, sample_count, length)
    resp = send_request_to_google_api(_PREDICT_API_ENDPOINT, req)
    return fetch_operation(_FETCH_API_ENDPOINT,resp['name'])


def image_to_video(_PREDICT_API_ENDPOINT,_FETCH_API_ENDPOINT,prompt, image, seed, aspect_ratio, sample_count, length):       
    req = compose_videogen_request(prompt, image, seed, aspect_ratio, sample_count, length)
    resp = send_request_to_google_api(_PREDICT_API_ENDPOINT, req)  
    return fetch_operation(_FETCH_API_ENDPOINT,resp['name'])



def video_generation(PROJECT_ID, MODEL, PROMPT,IMAGE = None, SAMPLE_COUNT=1,ASPECT_RATIO="16:9",LENGTH=6):
    
    _PREDICT_API_ENDPOINT = f'https://us-central1-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/{MODEL}:predictLongRunning'
    _FETCH_API_ENDPOINT = f'https://us-central1-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/{MODEL}:fetchPredictOperation'



    SEED = 0 # @param {type: 'number'}    
    
    if not IMAGE:
        resp = text_to_video(_PREDICT_API_ENDPOINT,_FETCH_API_ENDPOINT,PROMPT, SEED, ASPECT_RATIO, SAMPLE_COUNT, LENGTH)
        if 'error' in resp:
            return -1, resp['error']
        else:
            return 0, resp
    else:
        resp = image_to_video(_PREDICT_API_ENDPOINT,_FETCH_API_ENDPOINT,PROMPT, IMAGE, SEED, ASPECT_RATIO, SAMPLE_COUNT, LENGTH)
        if 'error' in resp:
            return -1, resp['error']
        else:
            return 0, resp

    
def retrieve_videos(res,sucess,prefix=None):
    # Decode and save the video
    if not prefix:
        prefix = 'video'
    if sucess == -1:
        print(f"video generation failed: {res}")
        return 0
    else:
        for idx, sample in enumerate(res['response']['generatedSamples']):
            encoded_video = sample['video']['encodedVideo']  # Extract Base64 string
            video_data = base64.b64decode(encoded_video)  # Decode Base64
            file_name = f"{prefix}_{idx}.mp4"  # Create a unique file name
            with open(file_name, "wb") as video_file:
                video_file.write(base64.b64decode(video_data))
            print(f"Saved video {idx} as {file_name}")
        return 0
