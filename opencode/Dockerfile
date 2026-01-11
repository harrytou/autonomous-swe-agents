FROM ghcr.io/anomalyco/opencode:1.1.13

# Install development tools needed by agents
RUN apk add --no-cache \
    git \
    python3 \
    py3-pip \
    nodejs \
    npm \
    curl \
    wget \
    bash \
    openssh-client

# Copy OpenCode configuration
COPY .config/opencode.json /root/.config/opencode/opencode.json
COPY .config/agent /root/.config/opencode/agent
