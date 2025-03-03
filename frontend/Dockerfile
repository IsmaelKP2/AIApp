FROM python:3.10.5-slim

RUN apt-get update && apt-get install -y curl
COPY requirements.txt app/requirements.txt
WORKDIR /app

RUN pip install -r requirements.txt
COPY . /app

EXPOSE 8501
CMD ["streamlit","run","streamlit_app.py"]