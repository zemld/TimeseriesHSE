FROM python:3.13-slim
WORKDIR /db_service
COPY . .
ENV PYTHONPATH="/db_service"
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main:db_manager", "--port=8002"]