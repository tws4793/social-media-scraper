import argparse, datetime, re, time
from scraper import Scraper
from multiprocessing import Pool
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class GooglePlayScraper(Scraper):
    els = {
        'name': 'X43Kjb',
        'date': 'p2TkOb',
        'rating': 'pf5lIe',
        'comment_fr': 'bN97Pc',
        'comment_wo': 'fbQN7e'
    }

    def dropdown_select_newest(self):
        # Locate the dropdown
        self.driver.find_element(
            By.XPATH, '//div[@class=\'jgvuAb Eic1df\']').click()
        self.driver.find_elements(
            By.XPATH, '//div[@class=\'OA0qNb ncFHed\']/div')[0].click()
        time.sleep(2)
        print('Dropdown Selected: ' + self.driver.find_element(
            By.XPATH, '//div[@class=\'jgvuAb Eic1df\']').text)

    def get_review(self, review):
        # Name, Date
        name = review.find_element(
            By.XPATH, './/span[@class=\'X43Kjb\']')
        date = review.find_element(
            By.XPATH, './/span[@class=\'p2TkOb\']')

        # Rating
        rating_text = review.find_element(
            By.XPATH, './/div[@class=\'pf5lIe\']/div')
        rating = re.search(
            r'\b\d+\b', rating_text.get_attribute('aria-label')).group()

        # Summary
        comment_summary = review.find_element(
            By.XPATH, './/span[@jsname=\'bN97Pc\']')  # collapsed text
        comment = review.find_element(
            By.XPATH, './/span[@jsname=\'fbQN7e\']') \
            if 'Full Review' in comment_summary.text else comment_summary

        return [name.text, date.text, str(rating), comment.text]
    
    def scroll_down(self):
        try:
            # Scroll down to bottom
            self.driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight)')
            
            # Click 'Show More' if present
            element = self.driver.find_element(
                By.XPATH, '//*[contains(text(),\'Show More\')]')
            self.driver.execute_script('arguments[0].click()', element)
        except Exception:
            time.sleep(1.5)

    def process(self, url, filename, scroll_threshold):
        self.access_page(url)

        time_start = datetime.datetime.now()
        print('Starting at...' + str(time_start))

        # Confirm the app to be scraped
        app_name = self.driver.find_element(
            By.XPATH, '//h1[@itemprop=\'name\']/span')
        print(app_name.text)

        self.dropdown_select_newest()

        # Get the data and start scrolling down again
        print('Start scraping')
        for i in range(scroll_threshold):
            try:
                for j in range(3):
                    self.scroll_down()

                # Get the existing reviews
                WebDriverWait(self.driver, 10,
                    ignored_exceptions=self.ignored_exceptions
                    ).until(EC.presence_of_element_located(
                        (By.XPATH, '//div[@jsname=\'fk8dgd\']/*'))
                )
                reviews = self.driver.find_elements(
                    By.XPATH, '//div[@jsname=\'fk8dgd\']/*')
                
                # Map the reviews and write to file
                with Pool(processes = 64) as pool:
                    reviews_list = pool.map(self.get_review,reviews)
                
                self.write_to_csv(filename, reviews_list)
                
                # Output Progress
                print(str(i+1), len(reviews), str(datetime.datetime.now() - time_start))

                # Remove all previous reviews
                self.driver.execute_script("document.querySelectorAll('[jscontroller=\"H6eOGe\"]').forEach(function(node) { node.parentNode.removeChild(node) } )")
            except Exception as e:
                print(e)
                print('Error occured at ' + str(i+1))
                time.sleep(2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', help='Define scroll threshold', type=int)
    parser.add_argument('-a', help='App ID', type=str)
    parser.add_argument('-f', help='Output File Name', type=str)
    args = parser.parse_args()

    url = 'https://play.google.com/store/apps/details?id=' + args.a + '&showAllReviews=true'

    gs = GooglePlayScraper()
    gs.process(url, args.f, args.t)

if __name__ == '__main__':
    main()