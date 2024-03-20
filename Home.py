"""Home"""

import streamlit as st

st.header("Introduction", divider=True)

st.markdown(
    """
  A project to explore various foundation models that have vision capabilities in Amazon Bedrock.
  
  - **Image Reader** uses `Claude 3 multimodal models` to interpret images or transcribe text in the images.
  - **Image Finder** uses `Titan multimodal embedding model` to find the similar images by text or image.
  - **Image Library** uses `ChromaDB` as the vector database for storing images embeddings.
  - **Image Generator** uses `Titan image generator model` to generate images.

  [Read Blog](https://medium.com/jackie-chens-it-workshop/image-reader-a-project-to-explore-claude-3-vision-capabilities-af9f2e0e9dea) | [Watch Demo](https://youtu.be/1GbYEl1WGhY) | [Raise Issue](https://github.com/jc1518/image-reader/issues)
  """
)
