FROM python:3.13-slim
WORKDIR /data_updater
COPY data_updater data_updater
COPY db_connection db_connection 
COPY moex moex
COPY logs logs
COPY logger.py .
COPY tickers.py .
ENV PYTHONPATH="/data_updater"
RUN pip install --no-cache-dir -r data_updater/requirements.txt
CMD ["python", "data_updater/data_updater.py"]