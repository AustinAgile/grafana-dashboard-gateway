FROM python:3.6-slim-stretch
RUN pip install kubernetes==6.0.0
RUN pip install aiohttp
COPY code/server.py /usr/src
COPY code/requirements.txt /usr/src
ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src
EXPOSE 5858
CMD [ "python", "-u", "server.py" ]