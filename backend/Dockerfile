FROM python:3.10

WORKDIR /app
COPY . /app

# Install uv and sync dependencies
RUN pip install uv
RUN uv venv recreate

# Alternatively, if you have a pyproject.toml and use uv as the environment manager:
RUN uv sync

# Start the FastAPI application with `uvicorn`
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
