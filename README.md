# Image Reader

## Introduction

A project to explore various foundation models that have vision capabilities in Amazon Bedrock.

- Image Reader uses `Claude 3 multimodal models` to interpret images or transcribe text in the images.
- Image Finder uses `Titan multimodal embedding model` to find the similar images by text or image.
- Image Library uses `ChromaDB` as the vector database for storing images embeddings.
- Image Generator uses `Titan image generator model` to generate images.

## Requirements

- Use `Python 3.11+`, and install dependencies: `pip install -r requirements.txt`.

- Default bedrock region is `us-west-2`, change the value of `bedrock_region` accordinly if you use other regions.

- Request access to `Claude 3 model` in Bedrock if you have not done that.

## Usage

Setup AWS credentials, then run `streamlit run Home.py`.

## Demo

https://youtu.be/1GbYEl1WGhY
