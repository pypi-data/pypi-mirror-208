import logging
import time
from selenium_assist.helpers import dump_and_exit
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains


def load_page(task, url, driver):
    logging.debug(task)
    try:
        driver.get(url)
    except Exception as e:
        dump_and_exit("Cannot load webpage, dumping source and exiting!", driver, exc=e)
    return


def wait_for_presence(task, xpath, driver, timeout=60, extra_timeout=0):
    logging.debug(task)
    try:
        element_present = EC.presence_of_element_located((By.XPATH, xpath))
        WebDriverWait(driver, timeout).until(element_present)
        time.sleep(extra_timeout)
    except TimeoutException:
        dump_and_exit(
            f"Timed out waiting for element presence ({xpath}), dumping source and exiting!",
            driver,
        )
    return


def wait_for_visibility(task, xpath, driver, timeout=60, extra_timeout=3):
    logging.debug(task)
    try:
        element_present = EC.visibility_of_element_located((By.XPATH, xpath))
        WebDriverWait(driver, timeout).until(element_present)
        time.sleep(extra_timeout)
    except TimeoutException:
        dump_and_exit(
            "Timed out waiting for element visibility, dumping source and exiting!",
            driver,
        )
    return


def click_element(task, xpath, driver):
    logging.debug(task)
    try:
        driver.find_element_by_xpath(xpath).click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        dump_and_exit("Cannot click on element, dumping source and exiting!", driver)
    return


def send_keys(task, xpath, keys, driver, extra_timeout=5):
    logging.debug(task)
    try:
        element_present = EC.element_to_be_clickable((By.XPATH, xpath))
        WebDriverWait(driver, extra_timeout).until(element_present)
        element = driver.find_element_by_xpath(xpath)
        element.clear()
        element.send_keys(keys)
        WebDriverWait(driver, extra_timeout).until(
            lambda browser: element.get_attribute("value") == keys
        )
    except Exception as e:
        dump_and_exit(
            "Cannot send keys on element, dumping source and exiting!", driver, exc=e
        )
    return


def hoover_over_element(task, xpath, driver):
    logging.debug(task)
    try:
        element = driver.find_element_by_xpath(xpath)
        action = ActionChains(driver)
        action.move_to_element(element).perform()
    except Exception as e:
        dump_and_exit(
            "Cannot hoover over element, dumping source and exiting!", driver, exc=e
        )
    return


def switch_to_iframe(task, xpath, driver, timeout=60, extra_timeout=0):
    logging.debug(task)
    try:
        element_present = EC.frame_to_be_available_and_switch_to_it((By.XPATH, xpath))
        WebDriverWait(driver, timeout).until(element_present)
        time.sleep(extra_timeout)
    except TimeoutException:
        dump_and_exit(
            "Timed out switching to iframe, dumping source and exiting!", driver
        )
    return


def get_table_data(task, xpath, driver):
    logging.debug(task)
    data = []
    try:
        for tr in driver.find_elements_by_xpath(xpath + "//tr"):
            tds = tr.find_elements_by_tag_name("td")
            if tds:
                data.append([td.text for td in tds])
    except Exception as e:
        dump_and_exit(
            "Cannot get table data, dumping source and exiting!", driver, exc=e
        )
    return data
