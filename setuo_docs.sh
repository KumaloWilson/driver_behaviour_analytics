#!/bin/bash

# Create necessary directories
mkdir -p app/view/static/css
mkdir -p app/view/templates

# Make the script executable
chmod +x setup_docs.sh

echo "Directory structure created successfully!"
echo "Now copy the HTML and CSS files to their respective directories:"
echo "- app/view/templates/api_docs.html"
echo "- app/view/static/css/api-docs.css"
