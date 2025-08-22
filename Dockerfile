# fetch the latest Superset image - we'll base our image on that
FROM apache/superset:4.1.2

# switch to root user
USER root

# install Postgres driver and flask-cors explicitly
RUN pip install psycopg2-binary flask-cors

# copy Superset config file and tell Superset where it is
COPY config.py /app/superset_config.py
ENV SUPERSET_CONFIG_PATH=/app/superset_config.py

# copy and inject custom JS file
COPY custom.js /app/superset/static/assets/custom.js
RUN SPA_FILE=/app/superset/templates/superset/spa.html && \
    CUSTOM_SNIPPET='  <script nonce="{{ csp_nonce() }}" src="/static/assets/custom.js"></script>' && \
    sed -i "/{%\s*block tail_js\s*%}/a $CUSTOM_SNIPPET" "$SPA_FILE"

# Install envsubst to help with env var substitution
RUN apt-get update && apt-get install -y gettext-base && rm -rf /var/lib/apt/lists/*

# copy and chmod script AS ROOT
COPY entry.sh /app/entry.sh
RUN chmod +x /app/entry.sh

# Now switch to non-root user
USER superset

CMD ["/app/entry.sh"]