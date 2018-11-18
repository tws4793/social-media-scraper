# Social Media Scraper

This is a Social Media Scraper, developed using Selenium for Python.

The codes used for this scraper are designed to work with Docker, although they can be modified to use your ChromeDriver.

## How to Use

First, start your instance of Docker and build the `Dockerfile` by running:

``` bash

docker build -t py-selenium .
```

Then start a standalone headless Chrome browser in a new Docker container by running:

``` bash

docker run --rm -d -p 4444:4444 --name pyselenium --network pyscraper selenium/standalone-chrome
```

### Google Play Store

For the Google Play Store, run this command to gain access to the scraper and perform the scraping operation:

``` bash

docker run --rm -v $(pwd):/usr/workspace -w /usr/workspace --network pyscraper py-selenium python gplay-scraper.py -t 200 -a com.grabtaxi.passenger -f gplay_grab
```

### Facebook

Further details to be provided at a later date.