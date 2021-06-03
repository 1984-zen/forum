FROM python:3.8.3
RUN apt-get update \
    && apt-get install ffmpeg libsm6 libxext6  -y \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        vim \
    && rm -rf /var/lib/apt/lists/* \
RUN mkdir /code
WORKDIR /code
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]