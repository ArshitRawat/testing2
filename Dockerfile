FROM debian:bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER=/usr/bin/chromedriver
ENV TESSERACT_CMD=/usr/bin/tesseract

# Install base deps
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg software-properties-common \
    libnss3 libxss1 libasound2 libatk-bridge2.0-0 libgtk-3-0 libgbm1 \
    tesseract-ocr python3 python3-pip

# Install Chrome (fixed version)
RUN wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y /tmp/chrome.deb || apt --fix-broken install -y && \
    rm /tmp/chrome.deb

# Install a matching ChromeDriver manually (known stable version)
RUN wget -q https://chromedriver.storage.googleapis.com/124.0.6367.91/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    rm chromedriver_linux64.zip

# Set up app
WORKDIR /app
COPY . /app

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8080
CMD ["python3", "rgpv_scraper.py"]
