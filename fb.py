import argparse, datetime, itertools, os, re, time
from concurrent.futures import ThreadPoolExecutor, Future
from dotenv import load_dotenv
from bs4 import BeautifulSoup as BS
from scraper import Scraper
from multiprocessing import Process
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class FacebookScraper(Scraper):
    def login(self):
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
    
    def access_group(self):
        pool = ThreadPoolExecutor(max_workers=2)
        # links = []

        pool.submit(self.extract_posts)
        time.sleep(30)
        pool.submit(self.extract_comments)

        # Process(target=self.extract_posts).start()
        # proc_comments = Process(target=self.extract_comments)
        
        # proc_comments.start()

        # proc_comments.join()

    def extract_posts(self):
        self.access_page(self.url + '?sorting_setting=RECENT_ACTIVITY')

        for i in range(self.to):
            self.driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(2.5)
            print('Scrolled down ' + str(i + 1) + 'x')

            soup = BS(self.driver.page_source, 'html.parser')
            self.links = soup.find_all('a', class_="_5pcq")

    def extract_comments(self):
        searched = [re.findall(r'permalink\/\d+', str(link))[0] for link in self.links if 'permalink' in str(link)]
        ids = [iden[10:] for iden in searched]

        for i in ids:
            url = self.url[:8] + 'm' + self.url[11:] + '?view=permalink&id=' + i
            self.access_page(url)
            soup = BS(self.driver.page_source, 'html.parser')

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
            self.url = 'https://www.facebook.com/groups/' + name
            self.filename = 'data/' + name

                # if len(name) == 0:
                #     break
                # else:
            self.access_group()
        except Exception as e:
            raise e
        finally:
            print('Time Elapsed: ' + str(datetime.datetime.now() - time_start))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', help='Define scroll threshold', type=int)
    # parser.add_argument('-g', help='Group ID', type=str)
    args = parser.parse_args()

    # url = 'https://www.facebook.com/groups/' + args.g

    fb = FacebookScraper()
    fb.to = args.t
    fb.process()

if __name__ == '__main__':
    main()