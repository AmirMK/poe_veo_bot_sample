# `veo_calls` for Veo API

The `veo_calls` Python library provides a simple interface for using a video generation model in Google Cloud Platform (GCP). This document explains the usage of the library, its functions, parameters, and examples.

---

## Installation

To use the library, include `veo_calls.py` in your project directory and import it in your code:

```python
import veo_calls as veo
```

## Functions

### `video_generation`
This function generates videos based on a provided text prompt, optional image, and other specifications.

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

### `retrieve_videos`
This function retrieves and saves generated videos locally.

#### Parameters:
- **`res`** (dict):  
  Response object returned by `video_generation`.

- **`success`** (int):  
  Success flag from `video_generation`.

- **`prefix`** (str):  
  Filename prefix for saved videos.

#### Usage:
Saves videos as `{prefix}_video_{index}.mp4` for each generated sample.


  - On failure (`success = -1`):  
    Contains the error code and message.

## Examples

### 1. Generate Two Videos from Text Prompt
```python
PROJECT_ID = "XXX"
MODEL = "veo-001-preview-0815"
PROMPT = "a puppy playing with a flower in a garden"
SAMPLE_COUNT = 2
ASPECT_RATIO = "9:16"
LENGTH = 6
IMAGE = None

success, res = veo.video_generation(PROJECT_ID, MODEL, PROMPT, IMAGE, SAMPLE_COUNT, ASPECT_RATIO, LENGTH)
veo.retrieve_videos(res, success, prefix='my_text_vide')
```

### 2. Generate One Video from Image and Text
```python
with open("0.jpeg", "rb") as image_file:
    image_binary = image_file.read()

PROJECT_ID = "XXX"
MODEL = "veo-001-preview-0815"
PROMPT = "a puppy playing with a flower in a garden"
SAMPLE_COUNT = 1
ASPECT_RATIO = "9:16"
LENGTH = 6
IMAGE = {'image_binary': image_binary, 'mimeType': 'jpeg'}

success, res = veo.video_generation(PROJECT_ID, MODEL, PROMPT, IMAGE, SAMPLE_COUNT, ASPECT_RATIO, LENGTH)
veo.retrieve_videos(res, success, prefix='my_image_vide')
```


## Error Handling

- **Success (`success = 0`)**:  
  Videos are returned in binary format under `res['response']['generatedSamples']`.

- **Failure (`success = -1`)**:  
  Error details are provided in `res`, including code and message. Example:
  ```python
  print(res['error']['message'])

## Notes

- Ensure the model and project are correctly configured in GCP.  
- The function supports generating up to 4 video samples per call.  
- Currently, only two aspect ratios (`9:16` and `16:9`) and two durations (`3s` and `6s`) are supported.






