"""Image Generator"""

import os
import uuid
import base64

import streamlit as st

from lib import constants
from lib import utils

st.header("Image Generator 🖨️", divider=True)

utils.setup_storage()

prompt_window = st.sidebar.empty()

with prompt_window:
    with st.form("prompt", clear_on_submit=False, border=False):
        prompt = st.text_area("User prompt:")
        image_size = st.selectbox("Width, Height", options=constants.IMAGE_SIZE)
        cfg_scale = st.slider("CfgScale (randomness)", 1.1, 10.0, 8.0, 0.1, "%f")
        seed = st.slider("Seed (noise setting)", 0, 2147483646, 0, 1)
        image_numbers = st.select_slider(
            "Image numbers", options=constants.IMAGE_NUMBERS
        )
        submitted = st.form_submit_button("Generate")

if prompt and submitted:
    with st.spinner("Generating images..."):
        image_settings = ()
        base64_encoded_images = utils.generate_images(
            prompt=prompt,
            number_of_images=image_numbers,
            cfg_scale=cfg_scale,
            width=image_size[0],
            height=image_size[1],
            seed=seed,
        )
        images = [base64.b64decode(image) for image in base64_encoded_images]
    st.image(images)
