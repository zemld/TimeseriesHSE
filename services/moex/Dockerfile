FROM python:3.13-slim
WORKDIR /moex
COPY . .
ENV PYTHONPATH="/moex"
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main:moex_app"]