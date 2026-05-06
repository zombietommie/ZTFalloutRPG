#!/bin/bash
# A simple script to pull the latest code and restart the bot

echo "Pulling latest code from GitHub..."
git pull origin main

echo "Rebuilding and restarting the Docker containers..."
# --build ensures any new dependencies in requirements.txt or changes to the Dockerfile are applied
# -d runs it in the background
docker-compose up -d --build

echo "Bot updated successfully!"