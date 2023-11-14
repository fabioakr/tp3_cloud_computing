# Image creation using Dockerfile
docker build -t log8415-aws-tp2 .
# Create container using image and enviorment variables
docker run --env-file ./.env --name log8415 log8415-aws-tp2 "$1" "$2"
# Delete container
docker rm log8415
