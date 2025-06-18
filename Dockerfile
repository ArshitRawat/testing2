FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium-driver chromium tesseract-ocr libglib2.0-0 libnss3 libgconf-2-4 \
    libfontconfig1 libxss1 libappindicator1 libindicator7 libasound2 \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver
ENV TESSERACT_CMD=/usr/bin/tesseract

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
CMD ["python", "rgpv_scraper.py"]
