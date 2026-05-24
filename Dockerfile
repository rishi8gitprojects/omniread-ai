# 1. Use an official lightweight Python runtime as a parent image
FROM python:3.10-slim

# 2. Set environment variables to keep Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Install system dependencies required for building some python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy over the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your application code into the container
COPY . .

# 7. Expose the default Streamlit web port
EXPOSE 8501

# 8. Add a healthcheck so the cloud provider knows the app is healthy
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# 9. Command to run your app when the container starts
ENTRYPOINT ["streamlit", "run", "interface.py", "--server.port=8501", "--server.address=0.0.0.0"]