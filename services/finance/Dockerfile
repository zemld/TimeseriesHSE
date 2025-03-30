FROM python:3.13-slim
WORKDIR /finance
COPY . .
ENV PYTHONPATH="/finance"
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main:finance_service", "--host=0.0.0.0", "--port=8005"]