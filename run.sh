#!/bin/bash

chmod +x /app/wkhtmltox/bin/wkhtmltopdf
gunicorn --log-level=DEBUG --timeout 90 routes:app