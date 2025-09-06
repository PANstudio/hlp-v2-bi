# fetch the latest Superset image - we'll base our image on that
FROM apache/superset:4.1.2

# switch to root user
USER root

# install Postgres driver and flask-cors explicitly
RUN pip install psycopg2-binary flask-cors

# copy Superset config file and tell Superset where it is
COPY config.py /app/superset_config.py
ENV SUPERSET_CONFIG_PATH=/app/superset_config.py

# copy DB connection mutator file
COPY db_connection_mutator.py /app/db_connection_mutator.py

# make sure `/app` is part of pythonpath so that config file can find and import the mutator file
ENV PYTHONPATH="/app:${PYTHONPATH}"

# copy and inject custom JS file
COPY custom.js /app/superset/static/assets/custom.js
RUN SPA_FILE=/app/superset/templates/superset/spa.html && \
    CUSTOM_SNIPPET='  <script nonce="{{ csp_nonce() }}" src="/static/assets/custom.js"></script>' && \
    sed -i "/{%\s*block tail_js\s*%}/a $CUSTOM_SNIPPET" "$SPA_FILE"

# patch SS' sandbox eval, for custom map charts JS, to instead reference functions in our custom JS
# This is really terrible but sort of enforced - see dev docs
RUN sed -i 's/return a().runInNewContext(l,n,o),n\[r\]/return n[r] = hlp?.mapsCustomJs?.[t]?.(n);/' \
    /app/superset/static/assets/d9c803ba2f8f88aba3d2.chunk.js

# Install envsubst to help with env var substitution
RUN apt-get update && apt-get install -y gettext-base && rm -rf /var/lib/apt/lists/*

# copy and chmod script AS ROOT
COPY entry.sh /app/entry.sh
RUN chmod +x /app/entry.sh

# Now switch to non-root user
USER superset

CMD ["/app/entry.sh"]