FROM ghcr.io/astral-sh/uv:python3.12-alpine

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
COPY app/ ./app/

# Install dependencies using uv
RUN uv sync --frozen

# Expose port for FastAPI
EXPOSE 8000

# Run the application
CMD ["uv", "run", "fastapi", "run", "--host", "0.0.0.0", "--port", "8000"]
