#!/bin/bash

FILENAME="teleport-17.7.1.pkg"
URL="https://cdn.teleport.dev/$FILENAME"

echo "Downloading $FILENAME..."
curl -O --output-dir /Users/aceris/Downloads "$URL"

echo "Installing $FILENAME..."
sudo installer -pkg "/Users/aceris/Downloads/$FILENAME" -target /

echo "Cleaning up $FILENAME..."
rm "/Users/aceris/Downloads/$FILENAME"

echo "$FILENAME installed successfully."
