#!/usr/bin/env bash
host="$1"
shift
port="$1"
shift
timeout=20

until nc -z "$host" "$port"; do
  echo "Waiting for $host:$port..."
  sleep 1
  timeout=$((timeout - 1))
  if [ "$timeout" -eq 0 ]; then
    echo "Error: Timeout while waiting for $host:$port"
    exit 1
  fi
done
exec "$@"
