FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create templates directory
RUN mkdir -p templates

# Copy files - explicitly include templates
COPY templates ./templates/
COPY *.py *.sh ./

# Set proper permissions
RUN chmod +x start.sh

EXPOSE 2525 8025 8000

CMD ["./start.sh"]
