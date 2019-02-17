import argparse, datetime, itertools, os, re, time
from dotenv import load_dotenv
from bs4 import BeautifulSoup as BS
from scraper import Scraper
from multiprocessing import Pool
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class FacebookScraper(Scraper):
    def get_html_soup(self, url, to=1, verbose=False):
        self.access_page(url)
        
        for i in range(to):
            self.driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(2.5)
            print('Scrolled down ' + str(i + 1) + 'x')
        
        return BS(self.driver.page_source, 'html.parser')
    
    def login(self):
        # https://stackoverflow.com/questions/45635190/logging-facebook-using-selenium
        self.access_page('https://www.facebook.com/')
        load_dotenv()
        
        self.driver.find_element(
            By.XPATH, '//input[@id=\'email\']').send_keys(os.getenv('FB_EMAIL'))
        self.driver.find_element(
            By.XPATH, '//input[@id=\'pass\']').send_keys(os.getenv('FB_PASS'))
        self.driver.find_element(
            By.XPATH, '//input[starts-with(@id, \'u_0_\')][@value=\'Log In\']').click()
        
        WebDriverWait(self.driver, 20,
            ignored_exceptions=self.ignored_exceptions
            ).until(EC.presence_of_element_located(
                (By.XPATH, '//span[@class=\'_1vp5\']')
            )
        )
        
        name = self.driver.find_element(
            By.XPATH, '//span[@class=\'_1vp5\']')
        print('Logged in User: ' + name.text)
    
    def access_group(self, url, to=1):
        soup = self.get_html_soup(url + '?sorting_setting=RECENT_ACTIVITY', to)
        links = soup.find_all('a', class_="_5pcq")

        searched = [re.findall(r'permalink\/\d+', str(link))[0] for link in links if 'permalink' in str(link)]
        ids = [iden[10:] for iden in searched]

        for i in ids:
            self.extract_comments(url[:8] + 'm' + url[11:] + '?view=permalink&id=' + i)

    def extract_comments(self,url):
        soup = self.get_html_soup(url)

        comments = re.findall(r'comment-body\">(.+?)<', str(soup))
        date = re.findall(r'<abbr>(.+?)</abbr>', str(soup))

        print(len(comments))

        self.write_to_csv(self.filename,
                list(map(lambda c: [url, date[0], re.sub('<.*?>','',c)], comments))
        )
    
    def process(self, filename='', scroll_threshold=0):
        time_start = datetime.datetime.now()
        print('Starting at...' + str(time_start))

        self.filename = filename

        try:
            # Login
            self.login()
            print('Time Elapsed: ' + str(datetime.datetime.now() - time_start))

            # Access Page
            # while True:
                # name = str(input('Enter Name of Group: '))
            name = 'hitchsg'
            url = 'https://www.facebook.com/groups/' + name
            self.filename = 'data/' + name

                # if len(name) == 0:
                #     break
                # else:
            self.access_group(url,scroll_threshold)
            print('Time Elapsed: ' + str(datetime.datetime.now() - time_start))
        except Exception as e:
            raise e

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', help='Define scroll threshold', type=int)
    # parser.add_argument('-g', help='Group ID', type=str)
    args = parser.parse_args()

    # url = 'https://www.facebook.com/groups/' + args.g

    fb = FacebookScraper()
    fb.process(scroll_threshold=args.t)

if __name__ == '__main__':
    main()