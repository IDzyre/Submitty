
#!/usr/bin/env bash
set -euo pipefail

echo "Submitty E2E container entrypoint: starting services"

# Start PHP-FPM (try versioned then unversioned)
if command -v php-fpm${PHP_VER} >/dev/null 2>&1; then
  php-fpm${PHP_VER} -D
elif command -v php-fpm >/dev/null 2>&1; then
  php-fpm -D
elif service php${PHP_VER}-fpm start >/dev/null 2>&1; then
  true
else
  echo "ERROR: php-fpm not found/startable" >&2
  exit 1
fi

# Start a webserver: prefer nginx, fall back to apache2
if command -v nginx >/dev/null 2>&1; then
  nginx
elif command -v apache2ctl >/dev/null 2>&1; then
  apache2ctl start
else
  echo "ERROR: no webserver (nginx or apache2) found" >&2
  exit 1
fi

# Start Submitty daemons as the submitty_daemon user. Scripts must exist.
DAEMONS=(
  /usr/local/submitty/autograder/submitty_autograding_shipper.py
  /usr/local/submitty/autograder/submitty_autograding_worker.py
  /usr/local/submitty/sbin/submitty_daemon_jobs/submitty_daemon_jobs.py
)

for d in "${DAEMONS[@]}"; do
  if [ -f "$d" ]; then
    echo "Launching $d as submitty_daemon"
    if id submitty_daemon >/dev/null 2>&1; then
      su -s /bin/bash -c "nohup python3 '$d' >/var/log/$(basename "$d").log 2>&1 &" submitty_daemon
    else
      nohup python3 "$d" >/var/log/$(basename "$d").log 2>&1 &
    fi
  else
    echo "ERROR: required daemon script $d not found" >&2
    exit 1
  fi
done

echo "All services started; handing off to: $*"
exec "$@"
