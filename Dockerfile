FROM python:3.10-slim

# Set system configurations
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose the Streamlit target port
EXPOSE 8501

# Clean execution command bypassing shell wrappers
CMD ["streamlit", "run", "interface.py"]