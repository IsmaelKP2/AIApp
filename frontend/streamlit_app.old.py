import streamlit as st
import requests
from io import StringIO,BytesIO
from dotenv import load_dotenv
import os
import boto3
import logging
from botocore.exceptions import ClientError
from botocore.config import Config
import s3fs
from streamlit_oauth import OAuth2Component

# Load environment variables from the .env file (if present)
load_dotenv()
# Access environment variables as if they came from the actual environment
API_HOSTNAME = os.getenv('API_HOSTNAME')
ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
SESSION_TOKEN = os.getenv('SESSION_TOKEN')
AWS_BUCKET = os.getenv('AWS_BUCKET')
# Set Authorization environment variables
AUTHORIZE_URL = os.environ.get('AUTHORIZE_URL')
TOKEN_URL = os.environ.get('TOKEN_URL')
REFRESH_TOKEN_URL = os.environ.get('REFRESH_TOKEN_URL')
REVOKE_TOKEN_URL = os.environ.get('REVOKE_TOKEN_URL')
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
REDIRECT_URI = os.environ.get('REDIRECT_URI')
SCOPE = os.environ.get('SCOPE')


# Create an AWS Config object
my_config = Config(
    region_name = 'eu-west-2',
    signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

# Prompt creation
url = f"http://{API_HOSTNAME}:8000/ask/"
params = {
    "text": "How many cats ?"
}
headers = {
    "accept": "application/json",
}

# Creation of the s3 fs using s3fs 
fs = s3fs.S3FileSystem(
    anon=False, 
    key=f"{ACCESS_KEY}",
    secret=f"{SECRET_KEY}",)

def load_images():
    cols = st.columns(5)
    image_files = fs.glob("llms.ismaelpapa.com/*.jpeg")
    for i, image in enumerate(image_files):
        cols[i].image(fs.open(image, mode='rb').read(),width=150)
    return image_files, # manuscripts

def upload_file(file, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :return: True if file was uploaded, else False
    """

    # Upload the file
    s3_client = boto3.client(
        's3',
        aws_access_key_id=f"{ACCESS_KEY}",
        aws_secret_access_key=f"{SECRET_KEY}",
        config=my_config)

    try:
        response = s3_client.upload_fileobj(file, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    except FileNotFoundError:
        st.error('File not found.')
        return False
    return True

# Create OAuth2Component instance
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, REFRESH_TOKEN_URL, REVOKE_TOKEN_URL)

# Check if token exists in session state
if 'token' not in st.session_state:
    # If not, show authorize button
    result = oauth2.authorize_button("Authorize", REDIRECT_URI, SCOPE)
    if result and 'token' in result:
        # If authorization successful, save token in session state
        st.session_state.token = result.get('token')
        st.rerun()
else:
    # If token exists in session state, show the token
    token = st.session_state['token']
    #st.json(token)

    st.markdown("### Upload a picture of a cat and I will tell you how many cats there are in the picture")
    
    st.markdown("#### available pictures:")
    if st.button("refresh"):
        load_images()
    ## Load images from s3 in a grid
    images = load_images()
    
    uploaded_file = st.file_uploader("Choose a picture :",type=["jpg", "png"])
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
    
        with st.spinner('Uploading to s3...'):
            result = upload_file(uploaded_file,f"{AWS_BUCKET}",uploaded_file.name)
            if result:
                st.write('File was uploaded successfully')
            else:
                st.write('File was not uploaded successfully')
    
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

    if st.button("Refresh Token"):
        # If refresh token button is clicked, refresh the token
        token = oauth2.refresh_token(token)
        st.session_state.token = token
        st.rerun()









