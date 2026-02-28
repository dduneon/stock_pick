# Frontend Dockerfile - Next.js with Bun
FROM oven/bun:1-alpine

# Set working directory
WORKDIR /app

# Install system dependencies needed for node-gyp
RUN apk add --no-cache libc6-compat python3 make g++

# Copy package files first for better caching
COPY package.json bun.lock ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy the rest of the application code
# (This will be overridden by volume mount in dev, but needed for build)
COPY . .

# Expose the Next.js port
EXPOSE 3000

# Set environment variables
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Default command (can be overridden in docker-compose)
CMD ["bun", "run", "dev"]