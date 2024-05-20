#!/bin/bash

# AWS CLI needs to be installed and configured before running this script

# Specify your table configuration file
TABLE_CONFIG_FILE="./chalice/table_config.json"

# Extract the table name from the configuration file
TABLE_NAME=$(jq -r '.TableName' $TABLE_CONFIG_FILE)

# Delete the table if it exists
aws dynamodb delete-table --table-name $TABLE_NAME

# Wait until the table is deleted
aws dynamodb wait table-not-exists --table-name $TABLE_NAME

# Create a new table
aws dynamodb create-table --cli-input-json file://$TABLE_CONFIG_FILE

# Wait until the table is created
aws dynamodb wait table-exists --table-name $TABLE_NAME
