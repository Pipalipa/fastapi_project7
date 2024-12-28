# Use an official Python runtime as the base image
FROM python:3.9-slim

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
CMD ["sh", "-c", "uvicorn Scripts.api3:app --host 0.0.0.0 --port 8000 & streamlit run Scripts/app3.py --server.port 8501 --server.address 0.0.0.0"]