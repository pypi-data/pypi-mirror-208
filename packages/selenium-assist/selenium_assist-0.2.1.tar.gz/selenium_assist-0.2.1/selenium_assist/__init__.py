# This is so that you can import selenium_assist or import connect_webdriver from selenium_assist
# instead of from selenium_assist.managers import connect_webdriver

from .helpers import cleanup, save_screenshot, dump_and_exit
from .wrappers import (
    load_page,
    wait_for_presence,
    wait_for_visibility,
    click_element,
    send_keys,
    hoover_over_element,
    switch_to_iframe,
    get_table_data,
)
from .managers import connect_webdriver
