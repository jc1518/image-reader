FROM python:3.11.6-slim-bookworm

WORKDIR /image-reader

RUN apt-get update -y \
    && apt-get install -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY .streamlit/ .streamlit
COPY lib/ lib
COPY pages/ pages
COPY Home.py Home.py
RUN mkdir data

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
