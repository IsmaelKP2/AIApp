from model import model_pipeline
from typing import Union
import io
from fastapi import FastAPI, UploadFile
from PIL import Image
from traceloop.sdk import Traceloop

Traceloop.init()
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/ask")
def ask(text: str, file: UploadFile):
    #image = Image.open(io.BytesIO(content))
    image = Image.open(file.file)
    result = model_pipeline(text, image)
    return {"answer": result}