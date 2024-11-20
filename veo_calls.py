import requests
import time
import google.auth
import google.auth.transport.requests
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

    # Get access token calling API
    creds, project = google.auth.default()
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    access_token = creds.token

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }


    response = requests.post(api_endpoint, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def compose_videogen_request(prompt, image_binary, video_uri, gcs_uri, seed, aspect_ratio, sample_count, length):
    instance = {"prompt": prompt}
    if image_binary:    
        instance["image"] = {"bytesBase64Encoded": base64.b64encode(image_binary).decode(), "mimeType": "jpeg"}
    if video_uri:
        instance["video"] = {"gcsUri": video_uri}
    if gcs_uri =='':
        request = {
          "instances": [instance],
          "parameters": {"sampleCount": sample_count, "seed": seed, "aspectRatio": aspect_ratio, "durationSeconds": length}
      }
    else:
        request = {
          "instances": [instance],       
          "parameters": {"storageUri": gcs_uri, "sampleCount": sample_count, "seed": seed, "aspectRatio": aspect_ratio, "durationSeconds": length}

      }
    return request

def fetch_operation(_FETCH_API_ENDPOINT,lro_name):
    request = {
     'operationName': lro_name
  }
  # The generation usually takes 2 minutes. Loop 30 times, around 5 minutes.
  for i in range(30):
    resp = send_request_to_google_api(_FETCH_API_ENDPOINT, request)
    print(f'waiting...')
    if 'done' in resp and resp['done']:
        return resp
    time.sleep(10)

def text_to_video(_PREDICT_API_ENDPOINT,_FETCH_API_ENDPOINT,prompt, seed, aspect_ratio, sample_count, output_gcs, length):  
    req = compose_videogen_request(prompt, None, None, output_gcs, seed, aspect_ratio, sample_count, length)
    resp = send_request_to_google_api(_PREDICT_API_ENDPOINT, req)
    return fetch_operation(_FETCH_API_ENDPOINT,resp['name'])


def image_to_video(_PREDICT_API_ENDPOINT,_FETCH_API_ENDPOINT,prompt, image_gcs, seed, aspect_ratio, sample_count, output_gcs, length):  
    req = compose_videogen_request(prompt, image_gcs, None, output_gcs, seed, aspect_ratio, sample_count, length)
    resp = send_request_to_google_api(_PREDICT_API_ENDPOINT, req)  
    return fetch_operation(_FETCH_API_ENDPOINT,resp['name'])



def video_generation(PROMPT,SAMPLE_COUNT,IMAGE_BINARY = ""):
    
    PROJECT_ID = "...." # @param {type: 'string'}
    MODEL = "veo-001-preview-0815"

    _PREDICT_API_ENDPOINT = f'https://us-central1-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/{MODEL}:predictLongRunning'
    _FETCH_API_ENDPOINT = f'https://us-central1-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/{MODEL}:fetchPredictOperation'



    SEED = 0 # @param {type: 'number'}
    OUTPUT_GCS = ""#"gs://poe_test_demo" # @param {type: 'string'}
    VIDEO_GCS = "" # @param {type: 'string'}
    ASPECT_RATIO = "16:9" #@param ["9:16", "16:9"]   
    LENGTH = 6 #@param [3, 6]
    
    if IMAGE_BINARY=="":
        resp = text_to_video(_PREDICT_API_ENDPOINT,_FETCH_API_ENDPOINT,PROMPT, SEED, ASPECT_RATIO, SAMPLE_COUNT, OUTPUT_GCS, LENGTH)
    else:
        resp = image_to_video(_PREDICT_API_ENDPOINT,_FETCH_API_ENDPOINT,PROMPT, IMAGE_BINARY, SEED, ASPECT_RATIO, SAMPLE_COUNT, OUTPUT_GCS, LENGTH)

    return resp
    
