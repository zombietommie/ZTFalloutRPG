#!/bin/bash
# A simple script to pull the latest code and restart the bot

echo "Pulling latest code from GitHub..."
git pull origin master

echo "--- Showing latest commit on server ---"
git log -1 --pretty=format:"%h - %an, %ar : %s"
echo # for a new line

echo "--- Rebuilding and restarting the bot container ---"
# --force-recreate ensures the bot container is stopped and recreated
# --build rebuilds the image if the code has changed
docker-compose up -d --build --force-recreate bot

echo "--- Bot update process finished! ---"