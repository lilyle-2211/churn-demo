FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir \
    google-cloud-bigquery \
    pandas \
    numpy \
    xgboost \
    optuna \
    scikit-learn \
    pyyaml \
    pydantic \
    db-dtypes

# Copy trainer code and config
COPY trainer/ ./trainer/

# Set Python path to include trainer directory
ENV PYTHONPATH=/app:/app/trainer

# Set working directory to trainer so imports work
WORKDIR /app/trainer

# Default command
CMD ["python", "main.py"]
