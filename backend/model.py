from transformers import ViltProcessor, ViltForQuestionAnswering
import requests
from PIL import Image



processor = ViltProcessor.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
model = ViltForQuestionAnswering.from_pretrained("dandelin/vilt-b32-finetuned-vqa")

def model_pipeline(text: str,image):
    # prepare inputs
    encoding = processor(image, text, return_tensors="pt")

    # forward pass
    outputs = model(**encoding)
    logits = outputs.logits
    idx = logits.argmax(-1).item()
    print("Predicted answer:", model.config.id2label[idx])
    return model.config.id2label[idx]
