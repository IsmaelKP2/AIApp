FROM python:3.10.5-slim

COPY requirements.txt app/requirements.txt
WORKDIR /app

RUN pip install -r requirements.txt
COPY . /app

EXPOSE 80
CMD ["streamlit","run","streamlit_app.py","--server.port","80","browser.port","80"]