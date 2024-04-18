import os
import requests
from io import BytesIO
import gradio as gr
from requests_toolbelt import MultipartEncoder
from PIL import Image
import time

API_URL = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

def generate_image(prompt, negative_prompt, aspect_ratio, seed, api_key):
    headers = {
        "authorization": f"Bearer {api_key}",
        "accept": "image/*",
        "Content-Type": "multipart/form-data"
    }

    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "aspect_ratio": aspect_ratio,
        "seed": str(seed),
        "output_format": "png"
    }

    multipart_data = MultipartEncoder(fields=payload)
    headers["Content-Type"] = multipart_data.content_type

    response = requests.post(API_URL, headers=headers, data=multipart_data)

    if response.status_code == 200:
        image_data = response.content
        image = Image.open(BytesIO(image_data))
        return image, None
    else:
        error_data = response.json()
        error_message = error_data.get("message", "Unknown error")

        if "NSFW" in error_message:
            return None, "NSFW content detected. Please try a different prompt."
        elif "payment_required" in error_data.get("name", ""):
            return None, "You lack sufficient credits to make this request. Please purchase more credits at https://platform.stability.ai/account/credits and try again."
        elif "content_moderation" in error_data.get("name", ""):
            return None, "Your request was flagged by the content moderation system. Please try a different prompt."
        else:
            print("Error Details:")
            print(error_data)
            return None, error_message

def save_image(image):
    if not os.path.exists("results"):
        os.makedirs("results")
    timestamp = int(time.time())
    image_path = f"results/generated_image_{timestamp}.png"
    pil_image = Image.fromarray(image)
    pil_image.save(image_path)

with gr.Blocks() as demo:
    gr.Markdown("# Stable Diffusion 3.0 beta Generation GUI")
    gr.Markdown("GUI by Shmuel Ronen")

    with gr.Row():
        with gr.Column():
            prompt = gr.Textbox(label="Prompt")
            negative_prompt = gr.Textbox(label="Negative Prompt")
            aspect_ratio = gr.Dropdown(
                label="Aspect Ratio",
                choices=[
                    "4:5",
                    "21:9",
                    "16:9",
                    "3:2",
                    "5:4",
                    "1:1",
                    "4:5",
                    "2:3",
                    "9:16",
                    "9:21"
                ]
            )
            seed = gr.Number(label="Seed", value=0)
            api_key = gr.Textbox(label="API Key", type="password")
            generate_button = gr.Button("Generate Image")

        with gr.Column():
            output_image = gr.Image(label="Generated Image", interactive=False)
            error_output = gr.Textbox(visible=True)

    generate_button.click(
        fn=generate_image,
        inputs=[prompt, negative_prompt, aspect_ratio, seed, api_key],
        outputs=[output_image, error_output]
    )

    output_image.change(
        fn=save_image,
        inputs=[output_image],
        outputs=[]
    )

demo.launch(share=True)