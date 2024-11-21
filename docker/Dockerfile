# docker/Dockerfile

# Base image
FROM python:3.10-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements.txt from one level up
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the /src folder from one level up
COPY src ./src

# Run the Streamlit app
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]