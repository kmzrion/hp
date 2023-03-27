from bs4 import BeautifulSoup
import datetime 
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException



def hackerone_reports(driver):
    url = "https://hackerone.com/hacktivity?querystring=&filter=type:public&order_direction=DESC&order_field=latest_disclosable_activity_at&followed_only=false&collaboration_only=false"
    driver.get(url)

    # Wait for the reports to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sc-beqWaB.iUYvHw.hacktivity-item")))

    reports = driver.find_elements(By.CSS_SELECTOR, ".sc-beqWaB.iUYvHw.hacktivity-item")

    today = datetime.date.today()

    for report in reports:
        timestamp = report.find_element(By.CSS_SELECTOR, ".spec-hacktivity-item-timestamp").text

        if "day" not in timestamp:  # Assuming that the timestamp will have "day" in it if it's not today
            title = report.find_element(By.CSS_SELECTOR, "strong").text
            link = "https://hackerone.com" + report.find_element(By.CSS_SELECTOR, ".daisy-link.routerlink.daisy-link.hacktivity-item__publicly-disclosed.spec-hacktivity-item-title").get_attribute("href")
            reporter = report.find_element(By.CSS_SELECTOR, ".spec-user-mini-profile-tooltip > strong > a").get_attribute("href").split("/")[-1]
            team = report.find_element(By.CSS_SELECTOR, ".daisy-link.routerlink.daisy-link.daisy-link--major").get_attribute("href").split("/")[-1]
            status = report.find_element(By.CSS_SELECTOR, ".daisy-color-indicator.daisy-color-indicator--green.margin-5--right").find_element(By.XPATH, "./following-sibling::span").text
            severity = report.find_element(By.CSS_SELECTOR, ".sc-beqWaB.loyaaw.daisy-severity-label.spec-severity-rating.margin-4--left").text
            
            try:
                bounty = report.find_element(By.CSS_SELECTOR, ".spec-hacktivity-item-bounty").text
            except NoSuchElementException:
                bounty = "Not available"

            print(f"Title: {title}")
            print(f"Link: {link}")
            print(f"Timestamp: {timestamp}")
            print(f"Reporter: {reporter}")
            print(f"Team: {team}")
            print(f"Status: {status}")
            print(f"Severity: {severity}")
            print(f"Bounty: {bounty}")
            print("\n" + "=" * 80 + "\n")

def bugcrowd_reports(driver):
    url = "https://bugcrowd.com/crowdstream?filter=disclosures"
    driver.get(url)

    # Wait for the reports to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".bc-crowdstream-item")))

    reports = driver.find_elements(By.CSS_SELECTOR, ".bc-crowdstream-item")

    today = datetime.date.today().strftime("%d %b %Y")

    for report in reports:
        timestamp = report.find_element(By.CSS_SELECTOR, ".bc-crowdstream-item__date").text.replace("Disclosed on ", "")

        if today == timestamp:
            title = report.find_element(By.CSS_SELECTOR, "a[href^='/disclosures']").text
            link = "https://bugcrowd.com" + report.find_element(By.CSS_SELECTOR, "a[href^='/disclosures']").get_attribute("href")
            reporter = report.find_element(By.CSS_SELECTOR, "ul > li > a[href^='/']").text
            team = report.find_element(By.CSS_SELECTOR, "ul > li > a[href^='/']").text
            bounty = report.find_element(By.CSS_SELECTOR, ".bc-reward").text
            priority = report.find_element(By.CSS_SELECTOR, ".bc-badge").text

            print(f"Title: {title}")
            print(f"Link: {link}")
            print(f"Timestamp: {timestamp}")
            print(f"Reporter: {reporter}")
            print(f"Team: {team}")
            print(f"Bounty: {bounty}")
            print(f"Priority: {priority}")
            print("\n" + "=" * 80 + "\n")

HUNTR_URL = "https://huntr.dev/bounties/hacktivity"

def get_recent_bugs(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    bug_list = soup.find_all("div", class_="flex flex-row pr-2 first-of-type:pt-2 py-4")
    return bug_list

def display_bugs(bug_list):
    today = datetime.datetime.now().strftime("%b %-d")
    todays_bugs = [bug for bug in bug_list if today in bug.find("div", class_="text-sm font-medium opacity-50 float-right hidden md:inline-block").span.text.strip()]

    if not todays_bugs:
        print("No disclosed bugs found for today.")
        return

    print("Today's disclosed bugs:")
    for bug in todays_bugs:
        title = bug.find("a", id="report-link").text.strip()
        date = bug.find("div", class_="text-sm font-medium opacity-50 float-right hidden md:inline-block").span.text.strip()
        reporter = bug.find("a", class_="hover:text-blue-400 mr-1 underline").text.strip()
        repository = bug.find("a", class_="hover:text-blue-400 cursor-pointer ml-1 mr-1.5 underline").text.strip()
        language = bug.find("span", class_="mx-1.5").text.strip()
        severity = bug.find("div", class_="mx-1.5 hidden md:inline-flex flex-row").span.text.strip()
        cve = bug.find("a", class_="font-medium float-right hidden md:inline underline hover:text-blue-400 ml-2")
        cve = cve.text.strip() if cve else "N/A"

        print(f"\nTitle: {title}\nDate: {date}\nReporter: {reporter}\nRepository: {repository}\nLanguage: {language}\nSeverity: {severity}\nCVE: {cve}")
        

def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode (without GUI)
    driver = webdriver.Chrome(options=options)

    # Huntr
    print("Huntr:")
    bugs = get_recent_bugs(HUNTR_URL)
    display_bugs(bugs)

    # HackerOne
    print("\nHackerOne:")
    hackerone_reports(driver)

    # Bugcrowd
    print("\nBugcrowd:")
    bugcrowd_reports(driver)

    driver.quit()

if __name__ == "__main__":
    main()


