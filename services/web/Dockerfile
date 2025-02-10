FROM python:3.13-slim
WORKDIR /web
COPY . .
ENV PYTHONPATH="/web"
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main:webapp", "--port=8000"]