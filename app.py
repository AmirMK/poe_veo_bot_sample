import os
import logging
import requests
import base64
from fastapi import FastAPI
import fastapi_poe as fp
from typing import AsyncIterable
import veo_calls as veo

# Set up logging to ensure all logs are captured
logging.basicConfig(level=logging.INFO, force=True)

# Retrieve environment variables
poe_access_key = os.getenv("POE_ACCESS_KEY")
if not poe_access_key:
    raise ValueError("POE_ACCESS_KEY environment variable is not set.")

app = FastAPI()

class EnhancedVideoResponsePoeBot(fp.PoeBot):
    async def get_response(self, request: fp.QueryRequest) -> AsyncIterable[fp.PartialResponse]:
        try:
            # Process the latest message
            latest_message = request.query[-1]
            attachments = latest_message.attachments
            text_content = latest_message.content

            logging.info(f"Received message: {latest_message}")
            logging.info(f"Text content: {text_content}")
            logging.info(f"Attachments: {attachments}")

            # Configuration variables
            PROJECT_ID = os.getenv("PROJECT_ID")
            MODEL = "veo-001-preview-0815"
            SAMPLE_COUNT = 1
            ASPECT_RATIO = "9:16"
            LENGTH = 6

            def double_decode_video(encoded_video):
                """Double decode the Base64 encoded video."""
                try:
                    # First decode
                    intermediate_data = base64.b64decode(encoded_video)
                    # Second decode
                    binary_video = base64.b64decode(intermediate_data)
                    return binary_video
                except Exception as decode_error:
                    logging.error(f"Error during video decoding: {decode_error}")
                    return None

            # Handle attachments
            if attachments:
                for attachment in attachments:
                    content_type = attachment.content_type
                    logging.info(f"Attachment content type: {content_type}")
                    logging.info(f"Attachment object: {attachment}")

                    if not content_type.startswith("image/"):
                        yield fp.PartialResponse(text="Only text and image attachments are supported.")
                        return

                    # Download the image
                    response = requests.get(attachment.url)
                    if response.status_code != 200:
                        yield fp.PartialResponse(text="Error downloading the image.")
                        return

                    # Create the IMAGE dictionary
                    image_binary = response.content
                    mimeType = content_type.split("/")[-1]
                    IMAGE = {"image_binary": image_binary, "mimeType": mimeType}
                    
                    logging.info(f"Full prompot: {text_content} with image")
                    # Generate video
                    success, res = veo.video_generation(
                        PROJECT_ID, MODEL, text_content or "", IMAGE, SAMPLE_COUNT, ASPECT_RATIO, LENGTH
                    )
                    if success == -1:                        
                        yield fp.PartialResponse(
                            text=f"Video generation failed. {res}"
                        )
                        return

                    try:
                        encoded_video = res["response"]["generatedSamples"][0]["video"]["encodedVideo"]
                        binary_video = double_decode_video(encoded_video)
                        if not binary_video:
                            yield fp.PartialResponse(text="Error decoding the video.")
                            return
                    except (KeyError, IndexError):
                        yield fp.PartialResponse(text="Unexpected response from the video generation model.")
                        return

                    # Send video back to the user
                    await self.post_message_attachment(
                        message_id=request.message_id, file_data=binary_video, filename="generated_video.mp4"
                    )
                    return

            # Handle text-only messages
            if text_content:
                logging.info(f"Full prompot: {text_content} with image")
                success, res = veo.video_generation(
                    PROJECT_ID, MODEL, text_content, None, SAMPLE_COUNT, ASPECT_RATIO, LENGTH
                )
                if success == -1:                    
                    yield fp.PartialResponse(
                        text=f"Video generation failed. {res}"
                    )
                    return

                try:
                    encoded_video = res["response"]["generatedSamples"][0]["video"]["encodedVideo"]
                    binary_video = double_decode_video(encoded_video)
                    if not binary_video:
                        yield fp.PartialResponse(text="Error decoding the video.")
                        return
                except (KeyError, IndexError):
                    yield fp.PartialResponse(text="Unexpected response from the video generation model.")
                    return

                # Send video back to the user
                await self.post_message_attachment(
                    message_id=request.message_id, file_data=binary_video, filename="generated_video.mp4"
                )

        except Exception as e:
            logging.error(f"Error processing the request: {e}")
            yield fp.PartialResponse(text=f"Error processing the request: {e}")

    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        return fp.SettingsResponse(allow_attachments=False)

# Set up the Poe bot with the required access key
poe_bot = EnhancedVideoResponsePoeBot()
app = fp.make_app(poe_bot, access_key=poe_access_key)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
