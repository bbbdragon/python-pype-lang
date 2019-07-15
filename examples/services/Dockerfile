FROM python:3.6.7

ADD . /root/

WORKDIR /root

RUN pip install -r service_requirements.txt

EXPOSE 10004

CMD ["python3","classifier_service.py","data.csv"]
