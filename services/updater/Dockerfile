FROM python:3.13-slim
RUN apt-get update && \
    apt-get install -y gcc python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/
WORKDIR /updater
COPY . .
ENV PYTHONPATH="/updater"
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main:data_updater", "--host=0.0.0.0", "--port=8003"]