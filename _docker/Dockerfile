FROM python:3.6-slim-stretch
COPY code/server.py /usr/src
COPY code/requirements.txt /usr/src
RUN pip install -r /usr/src/requirements.txt
#ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src
EXPOSE 5858
CMD [ "python", "-u", "server.py" ]
