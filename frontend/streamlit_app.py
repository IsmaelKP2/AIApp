import streamlit as st
import requests
from io import StringIO,BytesIO

url = "http://backend:8000/ask/"
params = {
    "text": "How many cats ?"
}
headers = {
    "accept": "application/json",
    # "Content-Type": "multipart/form-data"
}

st.markdown("### Upload a picture of a cat and I will tell you how many cats there are in the picture")


uploaded_file = st.file_uploader("Choose a picture :",type=["jpg", "png"])
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()

    # Convert bytes_data to BytesIO object
    bytes_io = BytesIO(bytes_data)
    st.image(bytes_io,width=300)

    # Prepare the files dictionary for the request
    files = {
        "file": (uploaded_file.name, bytes_data, uploaded_file.type)
    }

    response = requests.post(url, params=params, headers=headers, files=files)
    message = st.chat_message("assistant")
    if response.status_code == 200:
        message.write(f"The predicted answer is {response.json().get('answer')}")
    else:
        st.write("Error:", response.json())
