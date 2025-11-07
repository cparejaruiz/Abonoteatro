import json
import logging
import os
import smtplib
import time

from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from utils import Config, Logger

Logger()
logger = logging.getLogger('server')
config = Config()

ini_tt = time.time()
logger.info("Start web scrapping")

try:
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options, service=service)
    driver.get(config.get('abonoteatro_url'))
    logger.info(f"Page loaded: {driver.current_url}")
    # Guardar screenshot inicial para debug
    driver.save_screenshot('debug_step1_initial.png')
    logger.info("Screenshot saved as debug_step1_initial.png")
except Exception as e:
    logger.error(f"Error initializing browser: {e}")
    raise

# Close cookies
try:
    # Esperar un poco para que cargue el popup
    time.sleep(2)
    driver.save_screenshot('debug_step2_before_cookies.png')
    
    # Intentar encontrar y hacer clic en el botón de cookies
    # Probamos varios selectores posibles
    cookie_clicked = False
    selectors = [
        "//button[contains(text(), 'Denegar')]",
        "//button[contains(., 'Denegar')]",
        "//button[@class='cmplz-deny']",
        "//a[contains(text(), 'Denegar')]",
    ]
    
    for selector in selectors:
        try:
            logger.info(f"Trying selector: {selector}")
            button = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, selector)))
            button.click()
            cookie_clicked = True
            logger.info(f"Cookies denied using selector: {selector}")
            break
        except:
            continue
    
    if not cookie_clicked:
        logger.warning("Could not find cookies button with any selector")
    
    time.sleep(1)
    driver.save_screenshot('debug_step3_after_cookies.png')
    
except Exception as e:
    logger.warning(f"Error with cookies banner: {e}")
    driver.save_screenshot('debug_step3_cookies_error.png')

# Fill login form
try:
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.XPATH, "//input[@id='nabonadologin']"))).send_keys(config.get('abonoteatro_user'))
    driver.find_element("xpath", "//input[@id='contrasenalogin']").send_keys(config.get('abonoteatro_password'))
    driver.find_element("xpath", "//input[@value='Entrar']").click()
    logger.info("Login form submitted")
    time.sleep(3)  # Esperar a que cargue después del login
    driver.save_screenshot('debug_step4_after_login.png')
    logger.info(f"After login URL: {driver.current_url}")
except Exception as e:
    logger.error(f"Error during login: {e}")
    driver.save_screenshot('debug_step4_login_error.png')
    driver.quit()
    raise

# Get events
try:
    driver.save_screenshot('debug_step5_before_iframe.png')
    logger.info("Looking for iframe...")
    
    # Intentar encontrar el iframe
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    logger.info(f"Found {len(iframes)} iframes")
    
    if len(iframes) > 0:
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe")))
        logger.info("Switched to iframe")
        time.sleep(1)
        driver.save_screenshot('debug_step6_inside_iframe.png')
    else:
        logger.warning("No iframe found, trying to scrape directly")
    
    container = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.XPATH, "//div[@class='main-content container']")))
    logger.info("Container found")
    driver.save_screenshot('debug_step7_container_found.png')
    
    elements = container.find_elements("xpath", "//div[@class='row']")
    logger.info(f"Found {len(elements)} row elements")
    events = []
    for element in elements:
        tokens = element.text.splitlines()
        if len(tokens) >= 5:
            title = tokens[0].upper()
            if title != 'FECHA EVENTO':
                subtitle = tokens[1].upper() if len(tokens) == 6 else ''
                location = tokens[-4].upper()
                price = float(tokens[-2][:-1].replace(',', '.'))
                events.append({'title': title, 'subtitle': subtitle, 'location': location, 'price': price})
    logger.info(f"Scraped {len(events)} events from website")
except Exception as e:
    logger.error(f"Error scraping events: {e}")
    driver.save_screenshot('debug_step_error_scraping.png')
    driver.quit()
    raise
finally:
    driver.quit()

events = sorted(events, key=lambda e: e['title'])
events = sorted(events, key=lambda e: e['price'], reverse=True)

# Load old events
events_file_path = config.get('events_file')
if os.path.exists(events_file_path):
    with open(events_file_path) as input_file:
        old_events = json.load(input_file)
    logger.info(f"Loaded {len(old_events)} previously known events")
else:
    old_events = {}
    logger.info("No previous events file found, treating all events as new")

# Find new events
active_events = {}
new_events = []
for event in events:
    active_events[event['title']] = event
    if event['price'] >= config.get('events_threshold') and event['title'] not in old_events:
        new_events.append(event)

# Send new events by email
if len(new_events) > 0:
    logger.info(f"Found {len(new_events)} new events, sending notification email")
    mail_title = "Novedades Abonoteatro"
    body = f"{mail_title}:\n"
    for event in new_events:
        body += f"* {event['title']}, {event['subtitle']}, {event['location']}, {event['price']}€\n"
    
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = mail_title
    msg['From'] = config.get('gmail_user')
    msg['To'] = ', '.join(config.get('gmail_recipients'))
    
    try:
        with smtplib.SMTP_SSL(config.get('gmail_server'), config.get('gmail_port')) as server:
            server.login(config.get('gmail_user'), config.get('gmail_password'))
            server.sendmail(config.get('gmail_user'), config.get('gmail_recipients'), msg.as_string())
        logger.info("Email notification sent successfully")
    except Exception as e:
        logger.error(f"Error sending email: {e}")
else:
    logger.info("No new events found")

# Store events in file
try:
    with open(config.get('events_file'), 'w') as outfile:
        json.dump(active_events, outfile, indent=2, ensure_ascii=False)
    logger.info(f"{len(active_events)} events found and saved in {round(time.time() - ini_tt, 2)} seconds")
except Exception as e:
    logger.error(f"Error saving events to file: {e}")
