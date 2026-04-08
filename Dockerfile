# Auto-generated Dockerfile for eSim Tool Manager
# Generated on: 2026-04-09

FROM ubuntu:22.04

# Set non-interactive to avoid timezone prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive

# Install prerequisite tools and ca-certificates
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Add OpenModelica official apt repository (required — not in default Ubuntu repos)
RUN curl -fsSL https://build.openmodelica.org/apt/openmodelica.asc \
    | gpg --dearmor -o /usr/share/keyrings/openmodelica-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/openmodelica-keyring.gpg] \
    https://build.openmodelica.org/apt jammy release" \
    > /etc/apt/sources.list.d/openmodelica.list

# Update system and install all EDA tools
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
ENV KICAD_SYMBOL_DIR="/usr/share/kicad/library"
ENV OPENMODELICAHOME="/usr/lib/omc"
ENV PATH="$PATH:$NGSPICE_HOME/bin:$KICAD_SYMBOL_DIR/bin:$OPENMODELICAHOME/bin"

# Set default working directory
WORKDIR /workspace

# Provide a default command
CMD ["/bin/bash"]
