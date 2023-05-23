#!/bin/bash
image='austindarrow/dashboard:1.0'
current_year=(date +%Y)
current_month=(date +%m)

# Grab data from UTRC database using script. Output should be an excel file
#       e.g. utrc_report_2021-09-01_to_2021-10-01.xlsx
#       copy data to ./assets/data/monthly_reports

# Stop and remove the current docker container
docker ps -q | xargs docker stop
# docker ps -q | xargs docker stop | xargs docker rm
# docker image rm $image

# # Rebuild the image with the new data included (not needed, as data will be mounted rather than embedded in image)
# docker build -t $image .

# Restart the docker container (takes a couple minutes to spin up)
docker run --rm -d -p 8050:8050 -v $(pwd)/.:/app $image