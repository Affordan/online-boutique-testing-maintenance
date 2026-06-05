import os
import time
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


BASE_URL = os.getenv("ONLINE_BOUTIQUE_URL", "http://localhost:8080").rstrip("/")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
CHROME_BINARY_PATH = os.getenv("CHROME_BINARY_PATH")
SCREENSHOT_DIR = Path(__file__).resolve().parents[2] / "figures" / "testing"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def build_driver() -> webdriver.Chrome:
    options = Options()
    if CHROME_BINARY_PATH:
        options.binary_location = CHROME_BINARY_PATH
    if os.getenv("SELENIUM_HEADLESS", "0") == "1":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--disable-gpu")

    if CHROMEDRIVER_PATH:
        driver_path = Path(CHROMEDRIVER_PATH)
        if not driver_path.exists():
            raise FileNotFoundError(f"CHROMEDRIVER_PATH does not exist: {driver_path}")
        return webdriver.Chrome(service=Service(str(driver_path)), options=options)

    return webdriver.Chrome(options=options)


def save(driver: webdriver.Chrome, name: str) -> None:
    driver.save_screenshot(str(SCREENSHOT_DIR / name))


def click_first_product(driver: webdriver.Chrome, wait: WebDriverWait) -> None:
    selectors = [
        "a[href^='/product/']",
        ".hot-product-card a",
        ".product-card a",
    ]
    for selector in selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            elements[0].click()
            return
    raise AssertionError("No product link found on homepage")


def add_to_cart(driver: webdriver.Chrome, wait: WebDriverWait) -> None:
    candidates = [
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.XPATH, "//button[contains(., 'Add To Cart')]"),
        (By.XPATH, "//input[@type='submit' and contains(@value, 'Add')]"),
    ]
    for by, value in candidates:
        elements = driver.find_elements(by, value)
        if elements:
            elements[0].click()
            return
    raise AssertionError("Add to cart control not found")


def fill_checkout_form(driver: webdriver.Chrome) -> None:
    values = {
        "email": "test@example.com",
        "street_address": "1600 Amphitheatre Parkway",
        "zip_code": "94043",
        "city": "Mountain View",
        "state": "CA",
        "country": "United States",
        "credit_card_number": "4111111111111111",
        "credit_card_expiration_month": "12",
        "credit_card_expiration_year": "2030",
        "credit_card_cvv": "123",
    }

    for name, value in values.items():
        elements = driver.find_elements(By.NAME, name)
        if not elements:
            continue
        element = elements[0]
        if element.tag_name.lower() == "select":
            select = Select(element)
            try:
                select.select_by_visible_text(value)
            except NoSuchElementException:
                try:
                    select.select_by_value(value)
                except NoSuchElementException:
                    for option in select.options:
                        option_value = option.get_attribute("value")
                        if option_value:
                            select.select_by_value(option_value)
                            break
        else:
            element.clear()
            element.send_keys(value)


def submit_checkout(driver: webdriver.Chrome) -> None:
    candidates = [
        (By.XPATH, "//button[contains(., 'Place Order')]"),
        (By.XPATH, "//button[contains(., 'Place order')]"),
        (By.XPATH, "//input[@type='submit']"),
    ]
    for by, value in candidates:
        elements = driver.find_elements(by, value)
        if elements:
            elements[0].click()
            return
    raise AssertionError("Checkout submit control not found")


def main() -> None:
    driver = build_driver()
    wait = WebDriverWait(driver, 20)
    try:
        driver.get(BASE_URL)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        save(driver, "selenium_homepage.png")

        click_first_product(driver, wait)
        wait.until(lambda d: "/product/" in d.current_url)
        save(driver, "selenium_product_detail.png")

        add_to_cart(driver, wait)
        time.sleep(1)

        driver.get(f"{BASE_URL}/cart")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        save(driver, "selenium_cart.png")

        fill_checkout_form(driver)
        save(driver, "selenium_checkout.png")
        submit_checkout(driver)
        time.sleep(2)
        save(driver, "selenium_result.png")

        print("Selenium flow finished.")
    except TimeoutException as exc:
        save(driver, "selenium_error.png")
        raise RuntimeError("Timed out while running Selenium flow") from exc
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
