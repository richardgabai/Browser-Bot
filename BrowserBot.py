import os
import smtplib
import socket
import time
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from flask import Flask, render_template, request, redirect, url_for

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# ChromeDriver Path
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "path/to/chromedriver")

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
    try:
        driver = webdriver.Chrome(CHROMEDRIVER_PATH)
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
    except Exception as e:
        print(f"Error during Google search: {e}")
        return []

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

app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search', methods=['POST'])
def search():
    keywords = request.form.get('keywords').split(',')
    google_results = google_search(keywords)
    filtered_results = filter_results(google_results, purchase_keywords)
    return render_template('results.html', results=filtered_results)

def check_internet_connectivity():
    try:
        response = requests.get("https://www.google.com", timeout=5)
        if response.status_code == 200:
            print("Internet connection is active.")
            return True
    except requests.ConnectionError:
        print("No internet connection available.")
    return False

# Main Script Execution
if __name__ == "__main__":
    if not check_internet_connectivity():
        print("Please check your internet connection and try again.")
        exit(1)

    print("Starting Google Search Scraping...")
    google_results = google_search(keywords)

    print("Filtering Results...")
    filtered_google_results = filter_results(google_results, purchase_keywords)

    if filtered_google_results:
        print("Sending Email Notification...")
        email_body = format_results_for_email(filtered_google_results)
        send_email(
            subject="Browser Bot Alert: New Leads Found",
            body=email_body,
            recipient=EMAIL_ADDRESS
        )
    else:
        print("No relevant results found.")

    app.run(debug=True)
