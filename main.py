import os
import time
import shutil

import requests
from requests import exceptions as r_exc
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def load_images(links: list, number_of_image: int):
    driver = webdriver.Edge()
    for link in links:
        href = link.get_attribute('href')
        driver.get(href)
        driver.implicitly_wait(3.5)
        try:
            driver.find_element(
                By.CLASS_NAME, "CheckboxCaptcha-Anchor").click()
        except exceptions.NoSuchElementException:
            pass
        try:
            img_origin = WebDriverWait(driver, 7).until(
                ec.presence_of_element_located(
                    (By.CLASS_NAME, "MMImage-Origin"))
            )
        except exceptions.TimeoutException:
            print("No such element")
            time.sleep(2)
            continue
        img_link = img_origin.get_attribute('src')
        try:
            response = requests.get(img_link, timeout=10)
        except r_exc.ReadTimeout:
            print("The read operation timed out")
            time.sleep(3)
            continue
        with open(str(number_of_image).zfill(4) + '.jpg', 'wb') as f:
            f.write(response.content)
            print('Success')
            number_of_image += 1
            if (number_of_image > 10):
                break
    driver.quit()
    return number_of_image


def get_images(name: str):
    os.chdir(name)
    url = "https://yandex.ru/images/search?text="
    full_url = os.path.join(url, name)
    number_of_image = 0
    driver = webdriver.Edge()
    while True:
        try:
            driver.get(full_url)
            driver.implicitly_wait(0.5)
            driver.find_element(
                By.CLASS_NAME, "CheckboxCaptcha-Anchor").click()
        except exceptions.NoSuchElementException:
            print('No Captcha')
        body = driver.find_element(By.CSS_SELECTOR, 'body')
        for i in range(40):
            body.send_keys(Keys.PAGE_DOWN)
            try:
                driver.find_element(
                    By.CLASS_NAME, "CheckboxCaptcha-Anchor").click()
            except exceptions.NoSuchElementException:
                pass
            if i in range(25, 40):
                try:
                    full_url = driver.find_element(
                        By.CLASS_NAME, "button2").get_attribute('href')
                    break
                except exceptions.NoSuchElementException:
                    pass
            time.sleep(0.4)
        driver.implicitly_wait(5)
        img_links = driver.find_elements(By.CLASS_NAME, 'serp-item__link')
        if len(img_links) > 0:
            print(len(img_links))
            number_of_image = load_images(img_links, number_of_image)
            print("Page is done!")
            time.sleep(10)

        if number_of_image > 10:
            driver.quit()
            os.chdir('..')
            break


def make_folders(names: list):
    if not os.path.isdir('dataset'):
        os.mkdir('dataset')

    os.chdir('dataset')

    if os.path.isdir(names[0]) and os.path.isdir(names[1]):
        shutil.rmtree(names[0])
        shutil.rmtree(names[1])

    os.mkdir(names[0])

    os.mkdir(names[1])


def main():
    class1 = "rose"
    class2 = "tulip"
    make_folders((class1, class2))
    get_images(class1)
    time.sleep(30)
    get_images(class2)

main()


