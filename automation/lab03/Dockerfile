FROM python:3.12-slim

ENV TZ=Europe/Chisinau \
    PYTHONUNBUFFERED=1

# 1. Install cron and timezone data
RUN apt-get update \
    && apt-get install -y --no-install-recommends cron tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install the Python libraries required by the script
COPY requirements.txt /app/lab03/requirements.txt
RUN pip install --no-cache-dir -r /app/lab03/requirements.txt

# 2. Copy the script, the cron tasks and the entrypoint script
COPY currency_exchange_rate.py /app/lab03/currency_exchange_rate.py
COPY cronjob /etc/cron.d/currency_cron
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# 3. Configure cron: strip Windows line endings (CRLF), set permissions
#    and register the tasks in root's crontab
RUN sed -i 's/\r$//' /etc/cron.d/currency_cron /usr/local/bin/entrypoint.sh \
    && chmod 0644 /etc/cron.d/currency_cron \
    && chmod +x /usr/local/bin/entrypoint.sh /app/lab03/currency_exchange_rate.py \
    && crontab /etc/cron.d/currency_cron \
    && rm /etc/cron.d/currency_cron \
    && touch /var/log/cron.log

# 4-5. Start cron in the foreground (logs go to /var/log/cron.log)
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
