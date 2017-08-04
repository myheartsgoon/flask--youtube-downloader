#!/bin/bash

chmod +x /app/wkhtmltox/bin/wkhtmltopdf
gunicorn routes:app