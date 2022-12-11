ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}-slim-buster
ARG FOLDERPATH=/portcast_app
ARG ENTRYPATH=/portcast_app

COPY . ${FOLDERPATH} 
WORKDIR ${FOLDERPATH} 
RUN apt update && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

# after build-time env variables
# ENV FLASK_APP portcast_app/flask_app.py
# ENV FLASK_RUN_HOST=0.0.0.0
# ENV FLASK_RUN_PORT=8080

CMD ["python3", "-m", "flask", "run"]