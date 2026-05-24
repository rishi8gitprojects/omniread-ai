# 1. Use an official lightweight Python runtime as a parent image
FROM python:3.10-slim

# 2. Set environment variables to optimize Python performance inside Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy over the requirements file and install python dependencies directly
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your application code into the container
COPY . .

# 6. Expose the default Streamlit web port
EXPOSE 8501

# 7. Command to run your app when the container starts
ENTRYPOINT ["streamlit", "run", "interface.py", "--server.port=8501", "--server.address=0.0.0.0"]