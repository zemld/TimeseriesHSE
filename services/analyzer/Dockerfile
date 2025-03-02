FROM python:3.13-slim
WORKDIR /analyzer
COPY . .
# Removed: COPY ../../logger.py ./logger.py 
# (this is handled by volume mount in docker-compose)
ENV PYTHONPATH="/analyzer"
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main:analyzer", "--host=0.0.0.0", "--port=8004"]