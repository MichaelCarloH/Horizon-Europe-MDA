FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential python3-dev

COPY backend/ .

# Install uv (fast Python installer)
RUN pip install uv

# Use uv to install dependencies
RUN uv pip install --system -r requirements.txt
RUN uv pip install --system -r requirements-azure.txt

RUN chmod +x startup.sh

ENV AZURE_ENVIRONMENT=true
ENV RUNNING_IN_DOCKER=true

EXPOSE 8000

CMD ["./startup.sh"]