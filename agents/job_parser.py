from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import sys
import time
import os

# This script uses Selenium and BeautifulSoup to extract and save the job description
# from a LinkedIn job posting. It handles dynamic loading and captures debug info.

def extract_job_description(linkedin_url: str) -> str:
    """
    Uses Selenium to extract the job description from a LinkedIn job posting.
    """
    # Set up Selenium options for headless browsing
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Navigate to the provided LinkedIn job URL
    driver = webdriver.Chrome(options=options)
    driver.get(linkedin_url)

    # Wait for the dynamic content to fully load
    time.sleep(8)  # wait for dynamic content to load

    # Scroll to the middle of the page to trigger lazy loading
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
    time.sleep(1.5)

    # Scroll to the bottom to load more dynamic content
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # Try to click the 'See more' button to expand full job description
    try:
        see_more_button = driver.find_element(By.CLASS_NAME, "show-more-less-html__button")
        driver.execute_script("arguments[0].click();", see_more_button)
        time.sleep(2)
    except:
        print("⚠️ 'See more' button not found or already expanded")

    content = ""
    try:
        # Extract the inner HTML of the job description and format list items
        description_elem = driver.find_element(By.CLASS_NAME, "show-more-less-html__markup")
        html = description_elem.get_attribute("innerHTML")
        soup = BeautifulSoup(html, "html.parser")
        for li in soup.select("li"):
            li.insert_before("• ")
        content += soup.get_text(separator="\n", strip=True) + "\n"
    except:
        print("❌ Could not find job description container.")

    try:
        # Try to retrieve additional description content as a fallback
        container = driver.find_element(By.CLASS_NAME, "jobs-description")
        content += container.text
        print("⚠️ Appended fallback container: jobs-description")
    except:
        pass

    # Save a screenshot and full HTML of the page for debugging
    os.makedirs("output", exist_ok=True)
    driver.save_screenshot("output/debug_screenshot.png")
    with open("output/full_page_dump.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    driver.quit()
    return content

# Entry point: get job description from command line argument and save it
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Please provide a LinkedIn job URL.")
        sys.exit(1)
    url = sys.argv[1]
    description_text = extract_job_description(url)
    if description_text:
        print("\n📝 Job Description:\n")
        print(description_text)
        with open("output/raw_job_description.txt", "w", encoding="utf-8") as f:
            f.write(description_text)
        print("\n✅ Job description saved to output/raw_job_description.txt")
    else:
        print("⚠️ No job description found.")
