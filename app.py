import os
import logging
import requests
from fastapi import FastAPI
import fastapi_poe as fp
from typing import AsyncIterable
import veo_calls as vc

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

            if attachments:
                for attachment in attachments:
                    content_type = attachment.content_type
                    logging.info(f"Attachment content type: {content_type}")
                    logging.info(f"Attachment object: {attachment}")

                    if "image" in content_type:
                        # Handle image attachments
                        response = requests.get(attachment.url)
                        if response.status_code != 200:
                            yield fp.PartialResponse(text="Error downloading the image.")
                            return

                        # Generate a response for the image
                        image_binary_preview = response.content[:20]
                        if text_content:
                            rep = vc.video_generation(text_content,1,image_binary_preview)
                            yield fp.PartialResponse(
                                text=f"ok you send a text with image\nText: {text_content}\nImage preview: {image_binary_preview}"
                            )
                        else:
                            rep = vc.video_generation("",1,image_binary_preview)
                            yield fp.PartialResponse(
                                text=f"ok you send an image without text!!\nImage preview: {image_binary_preview}"
                            )
                        return
                    else:
                        # Handle non-image attachments
                        yield fp.PartialResponse(text="you can only have text and/or image")
                        return

            if text_content:
                # Handle text-only messages
                rep = vc.video_generation(text_content,1,"")
                yield fp.PartialResponse(text=f"ok you send a text??\nText: {text_content}")
        except Exception as e:
            logging.error(f"Error processing the request: {e}")
            yield fp.PartialResponse(text=f"Error processing the request: {e}")

    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        # Ensure the bot accepts attachments
        return fp.SettingsResponse(allow_attachments=True)

# Set up the Poe bot with the required access key
poe_bot = EnhancedVideoResponsePoeBot()
app = fp.make_app(poe_bot, access_key=poe_access_key)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
