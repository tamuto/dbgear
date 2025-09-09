# DBGear Editor Docker Image
FROM python:3.12-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# No additional system dependencies needed

# Create non-root user
RUN groupadd -r dbgear && useradd -r -g dbgear dbgear

# Set working directory
WORKDIR /app

# Copy application files
COPY --chown=dbgear:dbgear . .

# Install dbgear-editor (this will also install dbgear core as dependency)
RUN pip install --no-cache-dir .

# Copy entrypoint script
COPY --chown=dbgear:dbgear docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Create directories for configuration and data
RUN mkdir -p /app/data /home/dbgear/.dbgear \
    && chown -R dbgear:dbgear /app /home/dbgear

# Switch to non-root user
USER dbgear

# Create volumes for persistence
VOLUME ["/home/dbgear/.dbgear", "/app/data"]

# Expose port
EXPOSE 8000


# Set entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]