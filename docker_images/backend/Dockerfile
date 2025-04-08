# Use the official Python image from the Docker Hub
FROM python:3.9-slim   

# Install git
RUN apt-get update && apt-get install -y git

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 5000

ENTRYPOINT [ "python", "app.py" ]

# CMD [ "start.sh" ]