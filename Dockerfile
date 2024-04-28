FROM python:3.6 as base
COPY . "/home/ubuntu/"
WORKDIR "/home/ubuntu/"
RUN python3.6 -m pip install -r requirements.txt
EXPOSE 5001
ENTRYPOINT ["python3.6", "server.py"]
