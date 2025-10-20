FROM python:3.12-slim

WORKDIR /app

# Copy dependency file and install dependencies
COPY pyproject.toml ./
RUN pip install uv && uv pip install --system .

# Copy trainer code and config
COPY trainer/ ./trainer/

# Set Python path to include trainer directory
ENV PYTHONPATH=/app:/app/trainer

# Set working directory to trainer so imports work
WORKDIR /app/trainer

# Default command
CMD ["python", "main.py"]
