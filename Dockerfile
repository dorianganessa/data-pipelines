FROM python:3.11-slim

WORKDIR /app

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy requirements files
COPY real-estate-etl/requirements.txt .
COPY real-estate-sqlmesh/requirements.txt ./sqlmesh-requirements.txt

# Install dependencies
RUN /root/.local/bin/uv pip install -r requirements.txt
RUN /root/.local/bin/uv pip install -r sqlmesh-requirements.txt

# Copy project files
COPY real-estate-etl/ ./real-estate-etl/
COPY real-estate-sqlmesh/ ./real-estate-sqlmesh/

# Set build arguments
ARG WAREHOUSE_NAME
ARG MOTHERDUCK_TOKEN
ARG SCRAPE_URL
ARG TELEGRAM_BOT_API_KEY
ARG CHAT_ID
ARG CHAT_TAG

# Set environment variables
ENV WAREHOUSE_NAME=$WAREHOUSE_NAME
ENV MOTHERDUCK_TOKEN=$MOTHERDUCK_TOKEN
ENV SCRAPE_URL=$SCRAPE_URL
ENV TELEGRAM_BOT_API_KEY=$TELEGRAM_BOT_API_KEY
ENV CHAT_ID=$CHAT_ID
ENV CHAT_TAG=$CHAT_TAG

# Run the script
CMD ["python", "real-estate-etl/scan_properties.py"]