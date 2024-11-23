# Veo Bot for Poe.com - Repository Documentation

This repository provides a complete implementation of a bot using **Veo** for video generation, hosted on **Poe.com** and deployed via **Google Cloud Run**. Below is the detailed documentation for each component of the repository.

**Note:**  
The `app.py` code is designed to handle both text-to-video and image-to-video generation. However, by default, the bot settings have `allow_attachments` set to `False`, which disables image attachments. If users wish to enable image-to-video generation, they only need to change the `allow_attachments` setting to `True`. No additional modifications are required.

---

## File Descriptions

### 1. `app.py`
The main application file for setting up the Veo bot on Poe.com. This file uses the `veo_calls` library to interact with the Veo video generation model and manages the bot's behavior.

#### Key Features:
- Accepts user inputs (text and/or image) from Poe.com.
- Calls the Veo video generation model to create videos based on the inputs.
- Sends the generated video back to the user as an attachment.

#### Required Environment Variables:
- **`POE_ACCESS_KEY`**:  
  The access key required to authenticate the Poe bot.
  
- **`PROJECT_ID`**:  
  The Google Cloud Platform (GCP) project id where the Veo model is deployed.

#### Current Configuration:
The following parameters are hardcoded in the current implementation:
- **`MODEL`**: The Veo model name (e.g., `"veo-001-preview-0815"`).
- **`SAMPLE_COUNT`**: Number of videos to generate (currently set to `1`).
- **`ASPECT_RATIO`**: Aspect ratio of the video (currently set to `"9:16"`).
- **`LENGTH`**: Duration of the video in seconds (currently set to `6`).

#### Future Enhancements:
These hardcoded parameters (e.g., `MODEL`, `SAMPLE_COUNT`, `ASPECT_RATIO`, and `LENGTH`) can be modified to accept user inputs, allowing more flexibility and customization in video generation.

#### Integration with `veo_calls`:
The `app.py` file imports and uses the `veo_calls` library to:
- Handle API calls to the Veo video generation model.
- Process the generated videos for returning to the user.
- Perform error handling and ensure smooth bot operation.

This script provides the interface for deploying the bot on Poe.com using Cloud Run.

---

### 2. `veo_calls.py`
This library handles interactions with the Veo video generation API.

## Authentication

By default, the library assumes that the app is running within GCP. In this scenario, the library uses the default GCP authentication mechanism, which automatically authenticates the application using the service account attached to the GCP environment (e.g., Compute Engine, Cloud Run).

### Running Outside of GCP

If the app is deployed outside of GCP, authentication requires a service account key in JSON format. To enable this:
1. Generate a JSON key for the service account with the necessary permissions.
2. The `send_request_to_google_api` function in the library includes commented-out code for explicitly loading the credentials from a JSON key. Uncomment this section to use it for authentication when running the app outside of GCP.

#### Functions:
- **`video_generation`**: Generates videos based on a provided text prompt, optional image, and other specifications.

  #### Parameters:
  - **`PROJECT_ID`** (str):  
    The GCP project ID.

  - **`MODEL`** (str):  
    The video generation model name (e.g., `"veo-001-preview-0815"`).

  - **`PROMPT`** (str):  
    Text description of the video to generate.

  - **`IMAGE`** (dict or `None`):  
    If generating a video from an image, provide a dictionary:  
    ```python
    {'image_binary': image_binary, 'mimeType': mimeType}
    ```
    - **`image_binary`** (bytes):  
      Binary content of the image file.
    - **`mimeType`** (str):  
      MIME type of the image (e.g., `"jpeg"`).  
      If not using an image, set `IMAGE` to `None`.

  - **`SAMPLE_COUNT`** (int):  
    Number of videos to generate (up to 4).

  - **`ASPECT_RATIO`** (str):  
    Aspect ratio for the generated video. Options:  
    - `"9:16"`  
    - `"16:9"`

  - **`LENGTH`** (int):  
    Duration of the generated video in seconds. Options:  
    - `3`  
    - `6`

  #### Returns:
  - **`success`** (int):  
    Indicates the success or failure of the operation:  
    - `0`: Video generation successful.  
    - `-1`: Video generation failed.

  - **`res`** (dict):  
    - On success (`success = 0`):  
      Contains the list of generated video samples in binary format:  
      ```python
      res['response']['generatedSamples'][i]['video']['encodedVideo']
      ```
      where `i` is the index of the video sample.

    - On failure (`success = -1`):  
      Contains the error code and message.

- **`retrieve_videos`**: Retrieves and saves generated videos locally.

  #### Parameters:
  - **`res`** (dict):  
    Response object returned by `video_generation`.

  - **`success`** (int):  
    Success flag from `video_generation`.

  - **`prefix`** (str):  
    Filename prefix for saved videos.

  #### Returns:
  Saves videos as `{prefix}_video_{index}.mp4` for each generated sample.

#### Notes:
- See the examples provided in the file for usage of these functions.
- The functions include error handling for invalid or unsuccessful requests.

---

### 3. `Dockerfile`
Defines the containerization of the application for deployment on Google Cloud Run.

#### Key Steps:
- Uses Python as the base image.
- Installs dependencies from `requirements.txt`.
- Copies the application files (`app.py`, `veo_calls.py`, etc.) into the container.
- Specifies the command to run the FastAPI application using `uvicorn`.

#### Notes:
- Ensure the image is built using a valid `ACCESS_TOKEN` environment variable during deployment.

---

### 4. `requirements.txt`
Specifies the dependencies required for the application.

#### Key Libraries:
- `fastapi`: For building the API.
- `uvicorn`: For running the application server.
- `requests`: For handling HTTP requests.
- `google-cloud-storage`: For interacting with Google Cloud Storage.
- `fastapi-poe`: For Poe bot integration.


