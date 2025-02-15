#!/bin/bash

echo "Installing Dependecies"
pip install -r requirements.txt --break-system-packages
echo "Creating Env File"
touch .env
cat >> .env <<EOF
GOOGLE_SEARCH_API_KEY="{key}"
GOOGLE_SEARCH_ID="{id}"
LIST_DIR="lists"
REPORT_DIR="reports"
EOF
echo "Setting up reporting folders"
mkdir reports
echo "Finished."