#!/bin/bash

chmod +x /app/wkhtmltox/bin/wkhtmltopdf
gunicorn --timeout 90 routes:app