# STAGE 1: The Builder (Heavy, contains compilers and tools)
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
# Install dependencies into a specific local directory
RUN pip install --user --no-cache-dir -r requirements.txt

# STAGE 2: The Runtime (Lightweight and Secure)
FROM python:3.11-slim
WORKDIR /app

# Copy ONLY the installed dependencies from the builder stage
COPY --from=builder /root/.local /root/.local
# Copy our application code
COPY . .

# Ensure the local binaries are on the system PATH
ENV PATH=/root/.local/bin:$PATH

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]