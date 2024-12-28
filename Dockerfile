# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set environment variables for UTF-8 encoding
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy only necessary files to leverage Docker caching
COPY requirements.txt ./

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose necessary ports for FastAPI and Streamlit
EXPOSE 8000 8501

# Default command to run both FastAPI and Streamlit
CMD ["sh", "-c", "gunicorn -w 4 -k uvicorn.workers.UvicornWorker Scripts.api3:app --bind 0.0.0.0:8000 & streamlit run Scripts/app3.py --server.port 8501 --server.address 0.0.0.0"]