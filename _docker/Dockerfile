FROM python:3.6-slim-stretch
COPY code/server.py /usr/src
COPY code/requirements.txt /usr/src
RUN pip install -r /usr/src/requirements.txt --index-url https://artifactory.mattersight.local/artifactory/api/pypi/pypi.local/simple --extra-index-url https://artifactory.mattersight.local/artifactory/api/pypi/external-pypi/simple --trusted-host artifactory.mattersight.local
#ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src
EXPOSE 5858
CMD [ "python", "-u", "server.py" ]
