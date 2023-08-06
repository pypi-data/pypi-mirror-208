import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os
from CirclesVacanciesScrapers.database_vacancies import DatabaseVacancies


class MonsterComScraper:
    def __init__(self, position, location):
        self.driver = self.open_driver()
        self.position = position
        self.location = location
        self.df = []
        self.source = "monster"

    def open_driver(self):
        """
        In this code, os.getcwd() returns the current working directory, and os.path.join() is used to join the current
        directory with the filename of the ChromeDriver executable. This way, the code should work on any operating
        system, as long as the ChromeDriver executable is in the same directory as the Python script.
        """
        options = Options()
        options.add_experimental_option('detach', True)
        driver_path = os.path.join(os.getcwd(), 'chromedriver')
        driver = webdriver.Chrome(options=options, executable_path=driver_path)
        return driver

    def get_url(self, position, location):
        """Generate url from position and location"""
        template = 'https://www.monster.com/jobs/search?q={}&where={}&page=3&so=m.h.s'
        position = position.replace(' ', '+')
        location = location.replace(' ', '+')
        url = template.format(position, location)
        return url

    def launch_website(self, url):
        self.driver.get(url)
        time.sleep(2)

    def get_page_records(self, job_list):
        """Extract all cards from the page"""
        job_title = self.driver.find_element(By.XPATH, '//h1[@class = "headerstyle__JobViewHeaderTitle-sc-1ijq9nh-5 eetoNA JobViewTitle"]').text.strip()
        title = job_title.split("\n")
        company = self.driver.find_element(By.XPATH, '//h2[@class = "headerstyle__JobViewHeaderCompany-sc-1ijq9nh-6 dyxqrf"]').text.strip()
        cmpny = company.split("\n")
        location = self.driver.find_element(By.XPATH, '//div[@class = "detailsstyles__DetailsTableDetailBody-sc-1deoovj-5 eyvZUJ"]').text.strip()
        loc = location.split("\n")
        job_description = self.driver.find_element(By.XPATH, '//div[@class = "descriptionstyles__DescriptionBody-sc-13ve12b-4 djFvUg"]').text.strip()
        url = self.driver.current_url
        data = {'Job_Title': title[0], 'Company': cmpny[0], 'Location': loc[0], 'Job_Description': job_description, 'url': url}
        job_list.append(data)

    def page_scraping(self, num_of_jobs_required):
        scraped_jobs = []
        try:
            url = self.get_url(self.position, self.location)
            self.launch_website(url)
            jobs = self.driver.find_elements(By.XPATH, '//div[@class = "job-search-resultsstyle__JobCardWrapNew-sc-1wpt60k-6 exeHTM"]')
            for job in jobs:
                job.location_once_scrolled_into_view
                job.click()
                time.sleep(5)
                self.get_page_records(scraped_jobs)
                num_of_jobs_required -= 1
                if num_of_jobs_required == 0:
                    break

            df = pd.DataFrame(scraped_jobs)
            df.to_csv("Monster_jobs.csv")
            self.driver.quit()
            self.df = df
            data = DatabaseVacancies()
            data.add_data_to_mysql_database(df, self.source, self.location)
        except:
            print("FAILED TO SCRAPE JOBS")


if __name__ == '__main__':
    pass






