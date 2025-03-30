FROM python:3.13-slim
WORKDIR /electricity
COPY . .
ENV PYTHONPATH="/electricity"
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main:electricity_service", "--host=0.0.0.0", "--port=8007"]