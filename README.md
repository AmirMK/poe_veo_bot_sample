# Veo Bot Repository Documentation

This repository provides a complete implementation of a bot using **Veo** for video generation, hosted on **Poe.com** and deployed via **Google Cloud Run**. Below is the detailed documentation for each component of the repository.

---

## File Descriptions

### 1. `app.py`
This is the main application file that sets up the bot for Poe.com and integrates the `veo_calls` library to call the Veo video generation model.

#### Key Features:
- Accepts user inputs (text and/or image) via Poe's platform.
- Calls the Veo model to generate videos based on user inputs.
- Sends the generated videos back to the user as a response.

#### Notes:
- `veo_calls.py` is used as a library to handle Veo API calls.
- Environment variables like `POE_ACCESS_KEY` and `ACCESS_TOKEN` must be provided for proper functionality.

---

### 2. `veo_calls.py`
This library handles interactions with the Veo video generation API.

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


