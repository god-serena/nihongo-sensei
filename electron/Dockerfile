FROM node:20-bookworm

# Install system deps for Electron
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    libgtk-3-0 \
    libnss3 \
    libxss1 \
    libasound2 \
    libxtst6 \
    libx11-xcb1 \
    libdrm2 \
    libgbm1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxshmfence1 \
    fonts-liberation \
    libatk-bridge2.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgcc1 \
    libglib2.0-0 \
    libnspr4 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libxcb1 \
    libxkbcommon0 \
    libxkbfile1 \
    libxfixes3 \
    libxext6 \
    libxrender1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Electron source
COPY electron/package.json ./electron/package.json 2>/dev/null || true
COPY electron/ ./electron/

# Copy frontend build output
COPY frontend/dist ./frontend/dist

# Expose Electron dev port (typically 9229 for remote debugging)
EXPOSE 9229

CMD ["echo", "Electron is a native desktop app and should be run locally. Use this container only for testing Electron-specific features with xvfb if needed."]
