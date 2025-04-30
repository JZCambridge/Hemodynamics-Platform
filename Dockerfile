# Use official Ubuntu base image
FROM ubuntu:22.04

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    build-essential \
    ca-certificates \
    libgl1-mesa-glx \
    libglu1-mesa \
    libxt6 \
    libxext6 \
    libqt5widgets5 \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
ENV CONDA_DIR=/opt/conda
ENV PATH="$CONDA_DIR/bin:$PATH"
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py37_4.12.0-Linux-x86_64.sh -O miniconda.sh && \
    bash miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh && \
    conda clean -afy

# Copy environment file
COPY environment.yml /tmp/environment.yml

# update conda
RUN conda update -n base conda -y

# Create Conda environment
RUN conda env create -f /tmp/environment.yml && \
    conda clean -afy

# Set up working directory
WORKDIR /app

# Activate environment and set default command
ENV PYTHONUNBUFFERED=1
RUN echo "source activate VTK_Side37" > ~/.bashrc
ENV PATH /opt/conda/envs/VTK_Side37/bin:$PATH

# Default command (modify according to your needs)
CMD ["bash"]