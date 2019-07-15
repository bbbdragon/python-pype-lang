docker rm classifier_service
docker build -t classifier_service .
docker run -p 10004:10004 --name classifier_service classifier_service:latest
