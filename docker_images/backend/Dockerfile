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
COPY ./utils ./utils
COPY ./dict ./dict 
COPY ./app.py .
COPY ./start.sh .
COPY ./env.sh .
# RUN find . -name "*.bin" -delete

# Expose the port the app runs on
EXPOSE 8080

ENTRYPOINT [ "/bin/bash" ]

CMD [ "start.sh" ]