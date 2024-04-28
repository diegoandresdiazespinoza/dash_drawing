FROM python:3.11.4-bullseye
COPY . "/home/ubuntu/"
WORKDIR "/home/ubuntu/"
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN python3.11 -m pip install -r requirements.txt
EXPOSE 5003
ENTRYPOINT ["python3", "main.py"]
