#!/bin/bash

# Exit on any error
set -e

echo "Starting Credit Scoring Validator..."

# Create necessary directories
mkdir -p data reports/generated reports/archive results/responses

# Start the application with Gunicorn
echo "Starting Gunicorn server..."
exec gunicorn app:app --config gunicorn.conf.py
