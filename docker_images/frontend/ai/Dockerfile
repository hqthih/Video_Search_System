# Use a more recent Node.js LTS version
FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# # Install dependencies
# RUN npm install next react react-dom
# RUN npm install @google-cloud/storage --legacy-peer-deps
# RUN npm install date-fns

# Copy the rest of the application code
COPY . .

# Build the Next.js application
# RUN npm run build --verbose

# Expose the port the app runs on
EXPOSE 3000

# Start the Next.js application
CMD ["npm", "run", "dev"]