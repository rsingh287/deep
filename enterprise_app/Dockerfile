FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required for postgres and other heavy ML/trading libs
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY enterprise_app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire local_ai_gui codebase, as the enterprise_app relies on legacy engines
COPY . /app/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# The default command will run the FastAPI server
CMD ["uvicorn", "enterprise_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
