# Use mongodb/atlas as a base image
FROM mongodb/atlas

# Install EPEL repository and enable CodeReady Builder
RUN dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm && \
    dnf install -y dnf-plugins-core && \
    /usr/bin/crb enable

# Install Python 3.11 from source with necessary build tools
RUN dnf install -y \
    gcc \
    openssl-devel \
    bzip2-devel \
    libffi-devel \
    zlib-devel \
    wget \
    make \
    tar \
    gzip \
    findutils \
    && wget https://www.python.org/ftp/python/3.11.8/Python-3.11.8.tgz && \
    tar xzf Python-3.11.8.tgz && \
    cd Python-3.11.8 && \
    ./configure && \
    make -j$(nproc) && \
    make altinstall && \
    ln -sf /usr/local/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/local/bin/pip3.11 /usr/bin/pip3 && \
    cd .. && \
    rm -rf Python-3.11.8 Python-3.11.8.tgz

# Install other required packages
RUN dnf install -y \
    gcc \
    openssl-devel \
    libffi-devel \
    ca-certificates \
    make \
    rust \
    cargo && \
    dnf clean all

# Verify Python installation
RUN python3 --version && pip3 --version

# Upgrade pip first and install setuptools-rust
RUN pip3 install --upgrade pip && \
    pip3 install setuptools-rust

# Verify Python version
RUN python3 --version && pip3 --version

# Upgrade pip and setuptools
RUN pip3 install --upgrade pip setuptools wheel

# Install typing_extensions explicitly with latest version
RUN pip3 install --upgrade typing_extensions

# Install Python dependencies
RUN pip3 install passlib[bcrypt]

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the dependencies file
COPY requirements.txt /app/

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the app files
COPY . /app/

# Expose the port FastAPI will run on
EXPOSE 8000

RUN yum remove -y mongodb-atlas && \
    rm -rf /var/lib/mongodb* && \
    rm -rf /etc/mongodb* && \
    rm -f /etc/yum.repos.d/mongodb-org-*.repo && \
    yum clean all && \
    microdnf clean all

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
