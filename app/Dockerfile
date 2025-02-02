FROM python:3.13-slim
WORKDIR /app
COPY app app
COPY db_connection db_connection 
COPY moex moex
COPY logs logs
COPY logger.py .
COPY tickers.py .
ENV PYTHONPATH="/app"
RUN pip install --no-cache-dir -r app/requirements.txt
CMD ["python", "app/webapp.py"]