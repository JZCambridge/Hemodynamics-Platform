# Use official Ubuntu base image
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    QT_X11_NO_MITSHM=1 \
    QT_QPA_PLATFORM=xcb \
    CONDA_DIR=/opt/conda \
    PATH="/opt/conda/bin:${PATH}" \
    LIBGL_ALWAYS_SOFTWARE=1 \
    MESA_GL_VERSION_OVERRIDE=3.3 \
    DISPLAY=:0 \
    VTK_RENDERER=OpenGL2 \
    VTK_USE_OFFSCREEN=true \
    VTK_DEFAULT_RENDER_WINDOW_OFFSCREEN=1 \
    VTK_X11_USE_XCB=1 \
    LIBGL_ALWAYS_SOFTWARE=1 \
    MESA_GL_VERSION_OVERRIDE=3.3

# Install system dependencies with GUI support
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
    build-essential \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libgl1-mesa-dev \
    mesa-common-dev \
    libosmesa6-dev \
    libglu1-mesa \
    mesa-utils \
    mesa-utils-extra \
    libosmesa6 \
    libxt6 \
    libxext6 \
    libxrender1 \
    libxcursor1 \
    libxfixes3 \
    libxi6 \
    libqt5widgets5 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-randr0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    xauth \
    xvfb \
    x11-utils \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/* \
    # 修复swrast_dri.so路径
    && mkdir -p /usr/lib/dri \
    && ln -s /usr/lib/x86_64-linux-gnu/dri/swrast_dri.so /usr/lib/dri/swrast_dri.so

# Update CA certificates
RUN update-ca-certificates

# Install Miniconda - modified to ensure conda is available after installation
RUN wget --no-verbose --https-only https://repo.anaconda.com/miniconda/Miniconda3-py37_4.12.0-Linux-x86_64.sh -O miniconda.sh \
    && bash miniconda.sh -b -p /opt/conda \
    && rm miniconda.sh \
    && /opt/conda/bin/conda clean -afy

# Create and configure environment
RUN /opt/conda/bin/conda create -y -n VTK_Side37 python=3.7 \
    && echo "source activate VTK_Side37" >> ~/.bashrc

# Install Python packages
RUN /bin/bash -c "source /opt/conda/bin/activate VTK_Side37 && conda install -c conda-forge libstdcxx-ng gcc \
    && pip install --no-cache-dir \
    psutil \
    pyside2==5.15.2.1 \
    numpy==1.21.6 \
    simpleitk==2.0.2 \
    matplotlib==3.4.0 \
    opencv-python-headless==4.5.4.60 \
    scipy==1.7.3 \
    scikit-image==0.19.3 \
    vtk==9.2.6 \
    scikit-learn==1.0.2 \
    pandas==1.3.5 \
    more-itertools \
    meshio==5.3.4 \
    pyyaml==6.0 \
    pyradiomics==3.0.1 \
    pyvista==0.38.3 \
    pyvistaqt==0.9.1 \
    pyinstaller==5.8.0 \
    openpyxl==3.1.1 \
    networkx==2.6.3"

# Set working directory and add conda env to path
WORKDIR /app
ENV PATH="/opt/conda/envs/VTK_Side37/bin:${PATH}" \
    PYTHONPATH=/app

# Set up virtual framebuffer
RUN echo '#!/bin/bash\nXvfb :0 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &\nsleep 1\n\
# Verify OpenGL installation once Xvfb is running\n\
glxinfo | grep "direct rendering" || echo "Warning: OpenGL direct rendering not available"\n\
exec "$@"' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

# Verification command for Python imports (doesn't require display)
RUN python -c "import PySide2, vtk, matplotlib, skimage; print('Imports successful')"

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]