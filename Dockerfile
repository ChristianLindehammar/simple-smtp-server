FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY smtp_server.py .

EXPOSE 2525

CMD ["python", "smtp_server.py"]
