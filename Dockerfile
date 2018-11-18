FROM python:alpine

# update apk repo
#RUN ls /etc/apk/repositories
RUN mkdir -p /etc/apk/
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.8/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.8/community" >> /etc/apk/repositories

# install chromedriver
RUN apk update
RUN apk add chromium chromium-chromedriver

# install selenium
RUN pip install -U pip \
    beautifulsoup4 \
    python-dotenv \
    selenium \