# Dockerfile for Airflow with Databricks Integration
# Build image for Credit Card Fraud Detection ETL Pipeline

FROM apache/airflow:latest-python3.11

# Set environment
ENV AIRFLOW_HOME=/opt/airflow
ENV PYTHONUNBUFFERED=1

# Install system dependencies
USER root
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Copy requirements
COPY airflow/requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy DAGs
COPY airflow/dags ${AIRFLOW_HOME}/dags

# Copy DAG plugins
COPY airflow/plugins ${AIRFLOW_HOME}/plugins

# Create directories
RUN mkdir -p ${AIRFLOW_HOME}/logs \
    && mkdir -p ${AIRFLOW_HOME}/config

# Copy Airflow configuration
COPY airflow/config/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg

# Initialize Airflow database (will be run separately)
# RUN airflow db init

EXPOSE 8080

CMD ["airflow", "webserver"]
