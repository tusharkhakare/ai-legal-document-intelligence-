FROM python:3.11-slim

WORKDIR /app

# Install system libraries needed by OCR and image processing
RUN apt-get update && apt-get install -y \
    libxcb1 \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy all project source code and assets
COPY backend ./backend
COPY graph ./graph
COPY rag ./rag
COPY utils ./utils
COPY knowledge_base ./knowledge_base
COPY vector_store ./vector_store
COPY static ./static
COPY app.py .
COPY run.py .

RUN mkdir -p uploads

# Cloud platforms assign a dynamic PORT environment variable (default 8501)
ENV PORT=8501
ENV BACKEND_URL=http://127.0.0.1:8000
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 8501 8000

# Start script that launches both backend and frontend in one container
CMD ["python", "run.py"]
