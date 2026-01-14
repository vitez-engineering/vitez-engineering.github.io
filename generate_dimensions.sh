#!/bin/bash

# Define paths
IMAGE_DIR="./images"
OUTPUT_FILE="dimensions.json"

# Check if images directory exists
if [ ! -d "$IMAGE_DIR" ]; then
    echo "Error: Directory $IMAGE_DIR does not exist."
    exit 1
fi

# Start the JSON file
echo "{" > $OUTPUT_FILE

# Get list of images
FILES=$(find "$IMAGE_DIR" -maxdepth 1 -type f | grep -E -i "\.(jpg|jpeg|png|webp)$")
COUNT=$(echo "$FILES" | wc -l)
CURRENT=0

echo "Processing $COUNT images..."

for img in $FILES; do
    CURRENT=$((CURRENT + 1))
    FILENAME=$(basename "$img")
    
    # Get dimensions using ImageMagick identify
    DIMS=$(identify -format "%w %h" "$img")
    WIDTH=$(echo $DIMS | cut -d' ' -f1)
    HEIGHT=$(echo $DIMS | cut -d' ' -f2)
    
    # Calculate ratio and FORCE leading zero using printf
    # This avoids the ".750" issue that breaks JSON
    RATIO=$(awk "BEGIN {printf \"%.3f\", $WIDTH/$HEIGHT}")
    
    # JSON formatting: add a comma unless it's the last file
    if [ $CURRENT -eq $COUNT ]; then
        echo "  \"$FILENAME\": $RATIO" >> $OUTPUT_FILE
    else
        echo "  \"$FILENAME\": $RATIO," >> $OUTPUT_FILE
    fi
    
    echo -ne "Progress: $CURRENT/$COUNT\r"
done

# Close the JSON file
echo "}" >> $OUTPUT_FILE

echo -e "\nSuccess: $OUTPUT_FILE generated with valid JSON numbers."
