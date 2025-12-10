FROM python:3.13.7
WORKDIR /app
COPY . .
RUN pip install -r reqs.txt
CMD ["/bin/sh"]
