"""Home"""

import streamlit as st

from lib import utils
from lib import constants
from lib.prompt_library import crawl_prompt_list, crawl_prompt

st.header("Home", divider=True)

prompt_library = crawl_prompt_list()
prompt_list = prompt_library.keys()

st.sidebar.subheader("Playground")

model_id = st.sidebar.selectbox(
    label="Select model:", index=0, options=constants.MODEL_IDS
)
sample = st.sidebar.selectbox(
    label="Select a sample from prompt library:",
    index=0,
    options=prompt_list,
)

sample_description = st.sidebar.markdown(prompt_library[sample]["description"])

prompt = crawl_prompt((prompt_library[sample])["href"])


prompt_window = st.sidebar.empty()
response_window = st.empty()


with prompt_window:
    with st.form("prompt", clear_on_submit=False, border=False):
        system_prompt = st.text_area(
            label="System prompt:", height=350, value=prompt["system"]
        )
        user_prompt = st.text_area(
            label="User prompt:", height=350, value=prompt["user"]
        )
        submitted = st.form_submit_button("Submit")

with response_window:
    st.markdown(
        """
        This project is to explore various foundation models that have vision capabilities in Amazon Bedrock. It currently includes following features:

        - **Image Reader** uses `Claude 3 multimodal models` to interpret images or transcribe text in the images.
        - **Image Finder** uses `Titan multimodal embedding model` to find the similar images by text or image.
        - **Image Library** uses `ChromaDB` as the vector database for storing images embeddings.
        - **Image Generator** uses `Titan image generator model` to generate images.

        Addtionally, if you are new to prompt engineering. You can try sample prompts from [Anthropic prompt library](https://docs.anthropic.com/claude/prompt-library) in the playground.

        [Read Blog](https://medium.com/jackie-chens-it-workshop/image-reader-a-project-to-explore-claude-3-vision-capabilities-af9f2e0e9dea) | [Watch Demo](https://youtu.be/1GbYEl1WGhY) | [Raise Issue](https://github.com/jc1518/image-reader/issues)
        """
    )

if submitted:
    response = ""
    with response_window:
        with st.spinner("Reading..."):
            stream = utils.read_images_with_response_stream(
                model_id, system_prompt, [], user_prompt
            )
            for token in stream:
                if token == "message_start":
                    break
        for token in stream:
            response += token
            st.write(response.replace("$", "\$"))
