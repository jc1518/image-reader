"""Image Reader"""

import json
import base64

import boto3
import streamlit as st
from botocore.config import Config
from jinja2.nativetypes import NativeEnvironment


# Region and model config
bedrock_region = "us-west-2"
boto_config = {"max_attempts": 3, "mode": "standard"}
anthropic_version = "bedrock-2023-05-31"
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
model_args = {"temperature": 0, "max_tokens": 1000}
default_system_prompt = "You are a helpful assistant."
default_prompt = "What are in the picture?"


# Functions
session = boto3.Session(region_name=bedrock_region)
boto3_bedrock = session.client(
    service_name="bedrock-runtime",
    config=Config(retries=boto_config),
)


@st.cache_data(show_spinner=False)
def format_content(base64_encoded_images, query):
    """Format content"""
    content = []
    if base64_encoded_images:
        if len(base64_encoded_images) == 1:
            template_string = '{"type": "image", "source": {"type": "base64","media_type": "image/jpeg","data": "{{image}}"} }'
            image_content = (
                NativeEnvironment()
                .from_string(template_string)
                .render(image=base64_encoded_images[0])
            )
        else:
            for idx, image in enumerate(base64_encoded_images):
                template_string = '{"type": "text", "text": "Image {{number}}:" },{"type": "image", "source": {"type": "base64","media_type": "image/jpeg","data": "{{image}}"} }'
                image_content = (
                    NativeEnvironment()
                    .from_string(template_string)
                    .render(number=idx + 1, image=image)
                )
        content.append(image_content)
    content.append(
        {
            "type": "text",
            "text": query,
        }
    )
    return content


@st.cache_data(show_spinner=False)
def send_content(system, base64_encoded_images, query):
    """Send payload to bedrock claude 3"""
    content = format_content(base64_encoded_images, query)
    try:
        response = boto3_bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(
                {
                    "anthropic_version": anthropic_version,
                    "max_tokens": 2000,
                    "temperature": 0,
                    "system": system,
                    "messages": [{"role": "user", "content": content}],
                }
            ),
        )
        response_body = json.loads(response.get("body").read())
    except Exception as err:
        response_body = {"error": str(err)}
    return response_body


def read_images(system, images, query):
    """Describe the content of image"""
    base64_encoded_images = []
    images_size = ""
    for image in images:
        base64_encoded_image = base64.b64encode(image.getvalue()).decode("utf-8")
        base64_encoded_images.append(base64_encoded_image)
        images_size += f"{image.size // 1024} KB, "
    response = send_content(system, base64_encoded_images, query)
    if "error" in response:
        return response["error"]
    else:
        return (
            f"{response['content'][0]['text']}\n\n"
            f"----------------\n"
            f"Image Size: {images_size}"
            f"Model: {response['model']}, Input Tokens: {response['usage']['input_tokens']}, Output Tokens: {response['usage']['output_tokens']}"
        )


# UI
st.header("Image Reader 👀", divider=True)

system_prompt = st.sidebar.text_input("System prompt:", default_system_prompt)
prompt = st.sidebar.text_input("User prompt:", default_prompt)
take_photo = st.sidebar.toggle("📷")

source_window = st.sidebar.empty()
clear = st.sidebar.button("Clear", type="primary")

image_window = st.empty()
response_window = st.empty()

if clear:
    image_window.empty()
    response_window.empty()

with source_window:
    with st.form("image-source", clear_on_submit=False, border=True):
        if take_photo:
            images = [st.camera_input("Camera")]
        else:
            images = st.file_uploader(
                "Choose pictures", accept_multiple_files=True, type=["jpg", "png"]
            )
        submitted = st.form_submit_button("Submit")

with image_window:
    if submitted:
        if not images:
            st.sidebar.warning("No images are chosen, but I will do it for you anyway.")
        else:
            st.image(images)

with response_window:
    if submitted:
        with st.spinner("Reading images..."):
            response = read_images(system_prompt, images, prompt)
        st.write(response)
