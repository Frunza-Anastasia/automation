#!/bin/sh

create_log_file() {
    echo "Creating log file..."
    touch /var/log/cron.log
    chmod 666 /var/log/cron.log
    echo "Log file created at /var/log/cron.log"
}

monitor_logs() {
    echo "=== Monitoring cron logs ==="
    tail -f /var/log/cron.log
}

run_cron() {
    echo "=== Starting cron daemon ==="
    exec cron -f
}

# cron starts jobs with an almost empty environment, so the container
# variables (API_KEY, API_BASE_URL, TZ, ...) are saved to /etc/environment,
# which cron loads for every job.
env > /etc/environment
create_log_file
monitor_logs &
run_cron
