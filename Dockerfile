# 1. Python ka base image le rahe hain
FROM python:3.11-slim

# 2. Google Chrome aur zaroori tools install kar rahe hain (Scraping ke liye)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 3. Working directory set kar rahe hain
WORKDIR /app

# 4. requirements.txt copy karke libraries install kar rahe hain
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Baki saara code copy kar rahe hain
COPY . .

# 6. Port 8000 khol rahe hain (FastAPI ke liye)
EXPOSE 8000

# 7. Server start karne ki command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]