"""Image Helper"""

import os
import uuid
import json
import base64
import logging
import mimetypes

import boto3
import streamlit as st
import chromadb
from botocore.config import Config
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction
from jinja2.nativetypes import NativeEnvironment

from lib import constants

boto3.set_stream_logger(name="botocore.credentials", level=logging.ERROR)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

session = boto3.Session(region_name=constants.BEDROCK_REGION)
bedrock_runtime = session.client(
    service_name="bedrock-runtime",
    config=Config(retries=constants.BOTO_CONFIG),
)

accept = "application/json"
content_type = "application/json"


def setup_storage():
    """Setup local storage"""
    for data_storage in [
        constants.DATA_LOCATION,
        constants.VECTOR_LOCATION,
        constants.FILE_LOCATION,
        constants.TEMP_LOCATION,
    ]:
        if not os.path.exists(data_storage):
            os.mkdir(data_storage)


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
        response = bedrock_runtime.invoke_model_with_response_stream(
            modelId=model_id,
            accept=accept,
            contentType=content_type,
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


@st.cache_data(show_spinner=False)
def format_content_for_titan_mm_embed(base64_encoded_image=None, text_input=None):
    """Format body for Tian multimodal embedding"""
    body = {
        "embeddingConfig": {"outputEmbeddingLength": constants.OUTPUT_EMBEDDING_LENGTH}
    }
    if base64_encoded_image is not None:
        body["inputImage"] = base64_encoded_image
    if text_input is not None:
        body["inputText"] = text_input
    return json.dumps(body)


def generate_embeddings(body):
    """Generate embeding"""
    try:
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=constants.MM_EMBED_MODEL,
            accept=accept,
            contentType=content_type,
        )
        response_body = json.loads(response.get("body").read())
    except Exception as err:
        raise
    return response_body


def upsert_embedding_to_chroma(ids, embeddings, metadatas):
    """Add or update embedding to chroma"""
    client = chromadb.PersistentClient(constants.VECTOR_LOCATION)
    collection = client.get_or_create_collection(name=constants.COLLECTION_NAME)
    collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas)


def delete_embedding_from_chroma(ids):
    """Delete embedding from chroma"""
    client = chromadb.PersistentClient(constants.VECTOR_LOCATION)
    collection = client.get_or_create_collection(name=constants.COLLECTION_NAME)
    collection.delete(ids=ids)


def find_similar_image(
    query_embeddings=None, query_texts=None, n_results=constants.N_RESULTS
):
    """Find similar image"""
    client = chromadb.PersistentClient(constants.VECTOR_LOCATION)
    collection = client.get_or_create_collection(
        name=constants.COLLECTION_NAME,
        embedding_function=AmazonBedrockEmbeddingFunction(
            session=session, model_name=constants.MM_EMBED_MODEL
        ),
    )
    result = collection.query(
        query_embeddings=query_embeddings,
        query_texts=query_texts,
        n_results=n_results,
        include=["embeddings", "metadatas", "distances"],
    )
    image_ids = [metadata["image_id"] for metadata in result["metadatas"][0]]
    file_paths = [metadata["file_path"] for metadata in result["metadatas"][0]]
    distances = [distance for distance in result["distances"][0]]
    found_images = list(zip(image_ids, file_paths, distances))
    logger.info(f"The most similar images are {found_images}.")
    return found_images


def add_images_to_library(images):
    """Add image to library"""
    image_ids = []
    embeddings = []
    metadatas = []
    for image in images:
        image_name = f"{uuid.uuid4()}.png"
        if hasattr(image, "name"):
            image_name = image.name
        logger.info(f"Adding {image_name} to image library.")
        with open(os.path.join(constants.FILE_LOCATION, image_name), "wb") as f:
            f.write(image.getbuffer())
        image_ids.append(image_name)
        base64_encoded_image = base64.b64encode(image.getvalue()).decode("utf-8")
        body = format_content_for_titan_mm_embed(base64_encoded_image)
        embedding = generate_embeddings(body)["embedding"]
        embeddings.append(embedding)
        metadata = {
            "image_id": image_name,
            "file_path": f"{constants.FILE_LOCATION}/{image_name}",
        }
        metadatas.append(metadata)
    upsert_embedding_to_chroma(image_ids, embeddings, metadatas)


def get_images_in_library():
    """Get the sorted list of images library"""
    sorted_images_list = sorted(
        [
            os.path.join(constants.FILE_LOCATION, image)
            for image in os.listdir(constants.FILE_LOCATION)
            if mimetypes.guess_type(os.path.join(constants.FILE_LOCATION, image))[0]
            == "image/png"
        ]
    )
    return sorted_images_list


def delete_image_from_library(image_path):
    """Delete image from library"""
    logger.info(f"Deleting {image_path} from image library.")
    os.remove(image_path)
    image_id = image_path.split("/")[-1]
    delete_embedding_from_chroma(ids=[image_id])


def generate_images(prompt, **kwargs):
    """Generate images"""
    number_of_images = kwargs.get("number_of_images", constants.NUMBER_OF_IMAGES)
    quality = kwargs.get("quality", constants.QUALITY)
    cfg_scale = kwargs.get("cfg_scale", constants.CFG_SCALE)
    height = kwargs.get("height", constants.HEIGHT)
    width = kwargs.get("width", constants.WIDTH)
    seed = kwargs.get("seed", constants.SEED)
    try:
        request = json.dumps(
            {
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {"text": prompt},
                "imageGenerationConfig": {
                    "numberOfImages": number_of_images,
                    "quality": quality,
                    "cfgScale": cfg_scale,
                    "height": height,
                    "width": width,
                    "seed": seed,
                },
            }
        )
        response = bedrock_runtime.invoke_model(
            modelId=constants.IMAGE_GENERATOR_MODEL, body=request
        )
        response_body = json.loads(response.get("body").read())
        base64_image_data = response_body["images"]
    except Exception as err:
        raise
    return base64_image_data
