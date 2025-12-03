# Base image
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy all files
COPY . .

# Build Next app
RUN npm run build

# Expose port
EXPOSE 3000

# Run production server
CMD ["sh", "-c", "PORT=${PORT} npm start"]
