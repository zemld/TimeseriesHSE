FROM python:3.13-slim
WORKDIR /moex
COPY . .
COPY ../../logger.py ./logger.py
ENV PYTHONPATH="/moex"
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main:moex_app", "--host=0.0.0.0", "--port=8001"]