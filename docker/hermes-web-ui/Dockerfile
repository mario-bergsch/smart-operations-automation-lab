FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install --only=production

# Copy application
COPY . .

# Create vault mount point
RUN mkdir -p /vault

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8080/ || exit 1

# Start application
CMD ["npm", "start"]
