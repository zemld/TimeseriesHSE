FROM python:3.11-slim
WORKDIR /analyzer
COPY . .
ENV PYTHONPATH="/analyzer"
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p saved_models/cnn saved_models/rnn saved_models/tft
CMD ["uvicorn", "main:analyzer", "--host=0.0.0.0", "--port=8004"]