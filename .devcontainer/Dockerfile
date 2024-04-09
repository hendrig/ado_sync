FROM python:3.11

# Set up the working directory
WORKDIR /workspace

# Set the default shell to bash
SHELL ["/bin/bash", "-c"]

# Copy requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports for debugging (optional)
EXPOSE 3000 5000

# Start VS Code's default command (entrypoint)
ENTRYPOINT ["sleep", "infinity"]