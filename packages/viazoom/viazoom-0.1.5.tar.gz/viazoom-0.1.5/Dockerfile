FROM ubuntu:latest

# Install necessary packages
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    python3 \
    python3-dev \
    python3-pip \
    libssl-dev \
    libffi-dev \
    cargo \
    && rm -rf /var/lib/apt/lists/*

# Install Maturin
RUN pip3 install --no-cache-dir maturin
RUN pip3 install --upgrade maturin
RUN pip3 install patchelf

# Set the working directory to /io
WORKDIR /io

# Start the container with the command
CMD ["bash"]
