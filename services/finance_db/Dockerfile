FROM python:3.13-slim
WORKDIR /finance_db_servicedb_service
COPY . .
ENV PYTHONPATH="/finance_db_service"
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main:db_manager", "--host=0.0.0.0", "--port=8002"]