# Use an official Python runtime as a parent image
FROM python:3.8-slim as backend

# Set the working directory inside the container
WORKDIR /app

# Copy the pyproject.toml and uv.lock from the root folder
COPY pyproject.toml uv.lock ./

# Install uv environment and dependencies based on pyproject.toml
RUN pip install uv 
RUN apt-get update && apt-get install -y build-essential
# Ensure uvicorn is installed
RUN pip install uvicorn

RUN uv sync 

# Copy the entire backend directory into the container
COPY backend/ ./backend

# Expose port for FastAPI server
EXPOSE 8000

# Command to start the FastAPI server with uvicorn
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
