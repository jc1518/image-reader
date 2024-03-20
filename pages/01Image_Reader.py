"""Image Reader"""

import streamlit as st

from lib import constants
from lib import utils


st.header("Image Reader 👀", divider=True)

utils.setup_storage()

take_photo = st.sidebar.toggle("Use camera")
if take_photo:
    images = [st.camera_input("Camera")]
else:
    images = st.sidebar.file_uploader(
        "Choose pictures", accept_multiple_files=True, type=["jpg", "png"]
    )

prompt_window = st.sidebar.empty()
image_window = st.empty()
response_window = st.empty()

with prompt_window:
    with st.form("prompt", clear_on_submit=False, border=False):
        model_id = st.selectbox(
            label="Select model:", index=0, options=constants.MODEL_IDS
        )
        system_prompt = st.text_area("System prompt:", constants.DEFAULT_SYSTEM_PROMPT)
        prompt = st.text_area("User prompt:", constants.DEFAULT_PROMPT)
        if not take_photo:
            add_to_image_library = st.checkbox("Add to image library")
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
            stream = utils.read_images_with_response_stream(
                model_id, system_prompt, images, prompt
            )
            for token in stream:
                if token == "message_start":
                    break
        for token in stream:
            response += token
            st.write(response.replace("$", "\$"))
    if not take_photo:
        if images and add_to_image_library:
            utils.add_images_to_library(images)
