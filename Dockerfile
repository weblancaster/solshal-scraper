FROM python:3.6.4-alpine
MAINTAINER Michael Lancaster
RUN mkdir /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "./app.py"]