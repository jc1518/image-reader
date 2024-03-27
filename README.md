# Image Reader

## Introduction

A project to explore various foundation models that have vision capabilities in Amazon Bedrock.

- Image Reader uses `Claude 3 multimodal models` to interpret images or transcribe text in the images.
- Image Finder uses `Titan multimodal embedding model` to find the similar images by text or image.
- Image Library uses `ChromaDB` as the vector database for storing images embeddings.
- Image Generator uses `Titan image generator model` to generate images.

## Requirements

- Use `Python 3.11+`, and install dependencies: `pip install -r requirements.txt`.

- Default bedrock region is `us-west-2`, change the value of `BEDROCK_REGION` in [constant.py](./image-reader/lib/constants.py) accordingly if you use other region.

- Request access to `Claude 3 models` and `Titan models` in Bedrock if you have not done that.

## Use locally

Setup AWS credentials, then run `cd image-reader; streamlit run Home.py`

## Deploy to AWS

Setup AWS credentials, then run

- Customize the [config.yaml](./cdk/config.yaml)
- Install dependencies `cd cdk; npm install`
- Deploy `npx cdk deploy --require-approval never`

## Demo

- [Image-Reader](https://youtu.be/1GbYEl1WGhY)
- [Image-Finder](https://youtu.be/kEoj5funEnk)

## Blog

- [Image-Reader: A project to explore Claude 3 Vision Capabilities](https://medium.com/jackie-chens-it-workshop/image-reader-a-project-to-explore-claude-3-vision-capabilities-af9f2e0e9dea)
- [Prompt Engineering with Claude 3 Haiku](https://medium.com/jackie-chens-it-workshop/prompt-engineering-with-claude-3-haiku-93a6c97ff0c9)
- [Unleashing the Power of Generative AI: Building a Smart Image Library](https://medium.com/jackie-chens-it-workshop/unleashing-the-power-of-generative-ai-building-a-smart-image-library-1c845ccc1da4)
