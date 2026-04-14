# Auto-generated Dockerfile for eSim Tool Manager
# Generated on: 2026-04-11 04:00:07

FROM ubuntu:22.04

# Set non-interactive to avoid timezone prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive

# Update system and install necessary packages
RUN apt-get update && apt-get install -y \
    libxaw7-dev \
    libx11-dev \
    libreadline-dev \
    ngspice \
    libwxgtk3.0-gtk3-dev \
    python3 \
    kicad \
    cmake \
    gcc \
    g++ \
    openmodelica \
    && rm -rf /var/lib/apt/lists/*

# Configure Tool Environment Variables
ENV NGSPICE_HOME="/usr/share/ngspice"
ENV PATH="$PATH:$NGSPICE_HOME/bin"
ENV KICAD_SYMBOL_DIR="/usr/share/kicad/library"
ENV PATH="$PATH:$KICAD_SYMBOL_DIR/bin"
ENV OPENMODELICAHOME="/usr/lib/omc"
ENV PATH="$PATH:$OPENMODELICAHOME/bin"

# Set default working directory
WORKDIR /workspace

# Provide a default command
CMD ["/bin/bash"]
