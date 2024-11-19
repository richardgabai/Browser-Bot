from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import socket

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"

# Keywords to Track
keywords = [
    "Managed Detection & Response (MDR)",
    "Cybersecurity solution for SMB/SME",
    "threat monitoring solution for SMB/SME",
    "SIEM/SOAR for small business"
]
purchase_keywords = ["buy", "looking for", "need", "recommend"]

# Helper Function: Send Email
def send_email(subject, body, recipient):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Helper Function: Reverse IP Lookup
def reverse_ip_lookup(ip):
    try:
        return socket.gethostbyaddr(ip)
    except socket.herror:
        return "Unknown Host"

# Google Search Scraper
def google_search(keywords, pages=1):
    driver = webdriver.Chrome('path/to/chromedriver')  # Or Brave driver
    driver.get("https://www.google.com")
    search_results = []
    for keyword in keywords:
        search_box = driver.find_element(By.NAME, "q")
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        for _ in range(pages):
            time.sleep(2)
            results = driver.find_elements(By.CSS_SELECTOR, '.tF2Cxc')
            for result in results:
                title = result.find_element(By.TAG_NAME, 'h3').text
                link = result.find_element(By.TAG_NAME, 'a').get_attribute('href')
                search_results.append({'keyword': keyword, 'title': title, 'link': link})
            try:
                next_button = driver.find_element(By.ID, "pnnext")
                next_button.click()
            except:
                break
    driver.quit()
    return search_results

# LinkedIn Scraper (Simplified)
def linkedin_search(keywords):
    driver = webdriver.Chrome('path/to/chromedriver')  # Or Brave driver
    driver.get("https://www.linkedin.com/")
    # Simulate login (replace with real credentials)
    username = driver.find_element(By.ID, "username")
    password = driver.find_element(By.ID, "password")
    username.send_keys("your_email@example.com")
    password.send_keys("your_password")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(5)
    search_results = []
    for keyword in keywords:
        search_box = driver.find_element(By.XPATH, "//input[@placeholder='Search']")
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)
        posts = driver.find_elements(By.CSS_SELECTOR, '.search-result__info')
        for post in posts:
            try:
                title = post.find_element(By.TAG_NAME, 'h3').text
                link = post.find_element(By.TAG_NAME, 'a').get_attribute('href')
                search_results.append({'keyword': keyword, 'title': title, 'link': link})
            except:
                continue
    driver.quit()
    return search_results

# Filter Results by Intent
def filter_results(results, purchase_keywords):
    filtered = []
    for result in results:
        for keyword in purchase_keywords:
            if keyword.lower() in result['title'].lower():
                filtered.append(result)
    return filtered

# Format Results for Email
def format_results_for_email(results):
    body = "Here are the latest search results:\n\n"
    for result in results:
        body += f"Keyword: {result['keyword']}\n"
        body += f"Title: {result['title']}\n"
        body += f"Link: {result['link']}\n\n"
    return body

# Main Script Execution
if __name__ == "__main__":
    print("Starting Google Search Scraping...")
    google_results = google_search(keywords)
    print("Starting LinkedIn Scraping...")
    linkedin_results = linkedin_search(keywords)
    
    print("Filtering Results...")
    filtered_google_results = filter_results(google_results, purchase_keywords)
    filtered_linkedin_results = filter_results(linkedin_results, purchase_keywords)
    
    all_filtered_results = filtered_google_results + filtered_linkedin_results
    
    if all_filtered_results:
        print("Sending Email Notification...")
        email_body = format_results_for_email(all_filtered_results)
        send_email(
            subject="Browser Bot Alert: New Leads Found",
            body=email_body,
            recipient="your_email@gmail.com"
        )
    else:
        print("No relevant results found.")
