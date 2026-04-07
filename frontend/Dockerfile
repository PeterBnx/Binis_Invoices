ARG NODE_VERSION=24.14.0-alpine
 
FROM node:${NODE_VERSION} AS dev
 
# Set working directory inside the container
WORKDIR /app/frontend/
 
# Copy package files
COPY package*.json ./
 
# Install dependencies
RUN npm install
 
# Copy rest of the source code
COPY . .
 
# Ensure the "node" user owns the application files
RUN chown -R node:node /app
 
 
# Switch to the built-in non-root "node" user
USER node
 
 
# Expose Vite dev server port
EXPOSE 5173