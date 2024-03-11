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
    template_image_id = '{"type": "text", "text": "Image {{image_id}}:"}'
    template_image = '{"type": "image", "source": {"type": "base64","media_type": "image/jpeg","data": "{{image}}"} }'
    if base64_encoded_images:
        for idx, image in enumerate(base64_encoded_images):
            if len(base64_encoded_images) > 1:
                image_id = (
                    NativeEnvironment()
                    .from_string(template_image_id)
                    .render(image_id=idx + 1)
                )

                content.append(image_id)
            image_content = (
                NativeEnvironment().from_string(template_image).render(image=image)
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
        raise
    return response_body


def send_content_with_response_stream(system, base64_encoded_images, query):
    """Send payload to bedrock claude 3 with response stream"""
    content = format_content(base64_encoded_images, query)
    try:
        response = boto3_bedrock.invoke_model_with_response_stream(
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
        response_body = response.get("body")
    except Exception as err:
        raise
    return response_body


@st.cache_data(show_spinner=False)
def read_images(system, images, query):
    """Describe the content of image"""
    base64_encoded_images = []
    images_size = ""
    if not images:
        images_size = "0, "
    else:
        for image in images:
            base64_encoded_image = base64.b64encode(image.getvalue()).decode("utf-8")
            base64_encoded_images.append(base64_encoded_image)
            images_size += f"{image.size // 1024} KB, "
    response = send_content(system, base64_encoded_images, query)
    return (
        f"{response['content'][0]['text']}\n\n"
        f"----------------\n"
        f"Image Size: {images_size}"
        f"Model: {response['model']}, Input Tokens: {response['usage']['input_tokens']}, Output Tokens: {response['usage']['output_tokens']}"
    )


def read_images_with_response_stream(system, images, query):
    """Describe the content of image with response stream"""
    base64_encoded_images = []
    images_size = ""
    model = ""
    if not images or images == [None]:
        images_size = "0, "
    else:
        for image in images:
            base64_encoded_image = base64.b64encode(image.getvalue()).decode("utf-8")
            base64_encoded_images.append(base64_encoded_image)
            images_size += f"{image.size // 1024} KB, "
    response = send_content_with_response_stream(system, base64_encoded_images, query)
    if response:
        for event in response:
            chunk = event.get("chunk")
            if chunk:
                data = json.loads(chunk.get("bytes").decode())
                if data["type"] == "message_start":
                    model = data["message"]["model"]
                    yield ("message_start")
                if data["type"] == "content_block_delta":
                    yield (data.get("delta", {}).get("text", ""))
                if data["type"] == "message_stop":
                    metrics = data["amazon-bedrock-invocationMetrics"]
                    yield (
                        f"\n\n----------------\n"
                        f"*Image Size: {images_size}"
                        f"Model: {model}, Input Tokens: {metrics['inputTokenCount']}, Output Tokens: {metrics['outputTokenCount']}, "
                        f"Invocation Latency: {metrics['invocationLatency']} ms, First Byte Latency: {metrics['firstByteLatency']} ms.*"
                    )


# UI
st.header("Image Reader 👀", divider=True)

take_photo = st.sidebar.toggle("Use camera")
if take_photo:
    images = [st.camera_input("Camera")]
else:
    images = st.sidebar.file_uploader(
        "Choose pictures", accept_multiple_files=True, type=["jpg", "png"]
    )

prompt_window = st.sidebar.empty()

source_window = st.empty()
image_window = st.empty()
response_window = st.empty()

with prompt_window:
    with st.form("prompt", clear_on_submit=False, border=False):
        system_prompt = st.text_area("System prompt:", default_system_prompt)
        prompt = st.text_area("User prompt:", default_prompt)
        submitted = st.form_submit_button("Submit")

with image_window:
    if not take_photo:
        st.image(images)

if submitted:
    if not images or images == [None]:
        st.sidebar.warning(
            "No images are chosen, but I will do it for you anyway in case thats what you want."
        )
    response = ""
    with response_window:
        with st.spinner("Reading..."):
            stream = read_images_with_response_stream(system_prompt, images, prompt)
            for token in stream:
                if token == "message_start":
                    break
        for token in stream:
            response += token
            st.write(response.replace("$", "\$"))
