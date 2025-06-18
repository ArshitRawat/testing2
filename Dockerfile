FROM python:3.10-slim

# Install Chrome, Chromedriver, and Tesseract
RUN apt-get update && apt-get install -y \
    wget curl gnupg unzip fonts-liberation tesseract-ocr \
    libnss3 libxss1 libappindicator3-1 libasound2 \
    libatk-bridge2.0-0 libgtk-3-0 libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome manually
RUN wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y /tmp/chrome.deb && \
    rm /tmp/chrome.deb

# Install matching ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f 1) && \
    DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION") && \
    wget -q "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip" && \
    unzip chromedriver_linux64.zip && mv chromedriver /usr/bin/chromedriver && chmod +x /usr/bin/chromedriver && \
    rm chromedriver_linux64.zip

# Set environment variables
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER=/usr/bin/chromedriver
ENV TESSERACT_CMD=/usr/bin/tesseract

# Set workdir and copy code
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port and run
EXPOSE 8080
CMD ["python", "rgpv_scraper.py"]
