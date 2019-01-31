#!/bin/bash

chmod +x /app/wkhtmltox/bin/wkhtmltopdf
gunicorn -t 60 routes:app
