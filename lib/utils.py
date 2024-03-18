"""Image Reader"""

import json
import base64

import boto3
import streamlit as st
from botocore.config import Config
from jinja2.nativetypes import NativeEnvironment

from lib import constants


session = boto3.Session(region_name=constants.BEDROCK_REGION)
boto3_bedrock = session.client(
    service_name="bedrock-runtime",
    config=Config(retries=constants.BOTO_CONFIG),
)


@st.cache_data(show_spinner=False)
def format_content_for_claude3(base64_encoded_images, query):
    """Format content per claude 3 message format"""
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


def send_content_to_claude3_with_response_stream(
    model_id, system, base64_encoded_images, query
):
    """Send payload to bedrock claude 3 with response stream"""
    content = format_content_for_claude3(base64_encoded_images, query)
    try:
        response = boto3_bedrock.invoke_model_with_response_stream(
            modelId=model_id,
            body=json.dumps(
                {
                    "anthropic_version": constants.ANTHROPIC_VERSION,
                    "max_tokens": constants.MAX_TOKENS,
                    "temperature": constants.TEMPERATURE,
                    "system": system,
                    "messages": [{"role": "user", "content": content}],
                }
            ),
        )
        response_body = response.get("body")
    except Exception as err:
        raise
    return response_body


def read_images_with_response_stream(model_id, system, images, query):
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
    response = send_content_to_claude3_with_response_stream(
        model_id, system, base64_encoded_images, query
    )
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
