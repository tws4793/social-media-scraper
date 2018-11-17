import selenium.common.exceptions as se_ex
import csv, os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class Scraper:
    executor = 'http://pyselenium:4444/wd/hub'
    arguments = ['incognito', 'no-sandbox', 'disable-dev-shm-usage',
                'disable-extensions', 'headless', 'disable-gpu']

    def __init__(self, executor=executor, arguments=arguments, implicit_wait=5):
        self.executor = executor
        self.arguments = arguments
        self.ignored_exceptions = (se_ex.NoSuchElementException,
                se_ex.StaleElementReferenceException)

        self.setup(implicit_wait)
    
    def chrome_opts(self, arguments):
        ''' Chrome options
        '''
        opts = webdriver.ChromeOptions()
        for a in arguments:
            opts.add_argument('--' + a)

        return opts
    
    def setup(self,implicit_wait=5):
        ''' Setup the remote web driver
        '''
        self.driver = webdriver.Remote(
            command_executor=self.executor,
            desired_capabilities=DesiredCapabilities.CHROME,
            options=self.chrome_opts(self.arguments))
        self.driver.implicitly_wait(implicit_wait)
    
    def access_page(self, url):
        ''' Access the page
        '''
        self.driver.get(url)
        print(self.driver.current_url)
    
    def write_to_file(self, filename, output, ext='txt'):
        with open(filename + '.' + ext, 'w') as f:
            f.write(output)
            print('Written')

    def write_to_csv(self, filename, output, headers=[]):
        with open(filename + '.csv', 'a') as f:
            writer = csv.writer(f)
            if len(headers) != 0:
                writer.writerow(headers)
            writer.writerows(output)
            print('Written')