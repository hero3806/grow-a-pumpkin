# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /bot

# Install ffmpeg and dependencies
RUN apt-get update && apt-get install -y ffmpeg gcc && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot
CMD ["python", "main.py"]



EXPOSE 8080