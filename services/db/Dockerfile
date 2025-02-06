FROM python:3.13-slim
WORKDIR /db
COPY . .
ENV PYTHONPATH="/db"
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main::db_manager"]