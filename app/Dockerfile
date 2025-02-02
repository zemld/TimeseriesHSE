FROM python:3.13-slim
WORKDIR /app
COPY . .
COPY ../db_connection . 
COPY ../moex .
COPY ../logs .
ENV PYTHONPATH="/app"
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app/webapp.py"]