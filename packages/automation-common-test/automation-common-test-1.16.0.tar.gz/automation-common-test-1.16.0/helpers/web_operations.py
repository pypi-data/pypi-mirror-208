from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import logging as logger
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import *
from helpers.driver_manager import create_driver, create_wait, current_os

"""Class that wraps selenium functions to be used in UI automation tests
"""

wait_msg = "Locator --> {}"
_driver_wait = None


def create_driver_instance(browser_type, run_mode):
    global driver
    global _driver_wait
    driver = create_driver(browser_type, run_mode)
    _driver_wait = create_wait()
    
    
class WaitForDocReady(object):
    """Class that allows to verify if the document (page) is loaded
    """

    def __call__(self, driver: WebDriver):
        """Execute a script to validate if the document is in ready state

        Args:
            driver (WebDriver): webdriver

        Returns:
            bool: returns true if document state is 'complete'
    """
        page_state = driver.execute_script('return document.readyState;')
        return page_state == "complete"


def _setup_wrapper(wait_time=None, wait_for_load=False):
    """Setup some internal functionalites to use in each selenium wrapper function

    Args:
        wait_time (float, optional): Optional wait time if the default wait want to be skipped. Defaults to None.
        wait_for_load (bool, optional): Allow to wait for the page to load. Defaults to False.
    """
    global  _driver_wait
    # If wait time is specified it doesn't affect the wait for doc ready
    if wait_for_load:
        _driver_wait.until(WaitForDocReady())
    if wait_time:
        ignored_exceptions = (StaleElementReferenceException,)
        _driver_wait = WebDriverWait(driver, wait_time, ignored_exceptions=ignored_exceptions)


"""
------------------------------------------------------------------------
Elements Operations    
------------------------------------------------------------------------
"""


def click(locator, elem_name, wait_time=None):
    """Allow to execute a click in an element using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elem = _driver_wait.until(EC.element_to_be_clickable((locator[0], locator[1])),
                              wait_msg.format(locator))
    elem.click()
    logger.info(f"Clicked on {elem_name}")


def click_multiple(locator, elem_name, wait_time=None):
    """Allow to execute a multiple click in an some elements using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    # Click in all elements with same locator
    elements = _driver_wait.until(EC.presence_of_all_elements_located((locator[0], locator[1])),
                                  wait_msg.format(locator))
    for elem in elements:
        if elem.is_displayed():
            elem.click()
    logger.info(f"Clicked on elements {elem_name}")


def click_with_replace_value(locator, value, elem_name, wait_time=None):
    """Allow to execute a click in an element with dynamic locator using selenium

    Args:
        locator (tuple): tuple with locator type and locator format string
        value (str | list) values to replace in the locator
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    locator = locator[0], locator[1].format(*value)
    elem = _driver_wait.until(EC.element_to_be_clickable((locator[0], locator[1])),
                              wait_msg.format(locator))
    elem.click()
    logger.info(f"Clicked on : {elem_name} with replace value: {value}")


def click_first_visible_element(self, locator, elem_name, wait_time=None):
    """Allow to click in the first visible element using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elems = _driver_wait.until(EC.presence_of_all_elements_located((locator[0], locator[1])))
    for elem in elems:
        if elem.is_displayed() or elem.is_enabled():
            elem.click()
    logger.info(f"Clicked on {elem_name}")


def click_first_visible_element_replace_value(self, locator, value, elem_name, wait_time=None):
    """Allow to click in the first visible element with dynamic locator using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        value (str | list): values to replace in the locator
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    logger.info(f"Clicked first visible element: {elem_name} with replace value: {value}")
    locator = locator[0], locator[1].format(*value)
    elems = _driver_wait.until(EC.presence_of_all_elements_located((locator[0], locator[1])),
                               wait_msg.format(locator))
    for elem in elems:
        if elem.is_displayed():
            elem.click()
            return


def click_using_js(self, locator, elem_name, wait_time=None):
    """Allow to execute a click in an element with javascript using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elem = _driver_wait.until(EC.visibility_of_any_elements_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    driver.execute_script("arguments[0].click();", elem[0])
    logger.info(f"Clicked on {elem_name}")


def click_using_js_with_replace_value(self, locator, value, elem_name, wait_time=None):
    """Allow to execute a click in an element with javascript using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        value (str | list): values to replace in the locator
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    locator = locator[0], locator[1].format(*value)
    elem = _driver_wait.until(EC.visibility_of_any_elements_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    driver.execute_script("arguments[0].click();", elem[0])
    logger.info(f"Clicked on {elem_name}")


def click_using_js_no_wait(self, locator, elem_name):
    """Allow to execute a click in an element with javascript and no wait using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
    """
    _setup_wrapper(wait_for_load=True)
    elem = driver.find_element(locator)
    driver.execute_script("arguments[0].click();", elem)
    logger.info(f"Clicked on element: {elem_name}")


def click_using_js_no_wait_replace_value(self, locator, value, elem_name):
    """Allow to execute a click in an element with javascript and no wait with dynamic locator using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        value (str | list) values to replace in the locator
        elem_name (str): description of the element
    """
    _setup_wrapper(wait_for_load=True)
    elem = driver.find_element((locator[0], locator[1].format(value)))
    driver.execute_script("arguments[0].click();", elem)
    logger.info(f"Clicked on: {elem_name} with replace value: {value}")


def scroll_element_into_view(self, locator, wait_time=None):
    """Allow to scroll into an element using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    logger.info("Scrolling element into view")
    elem = _driver_wait.until(EC.presence_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    driver.execute_script("arguments[0].scrollIntoView();", elem)


def scroll_element_into_view_with_replace_value(self, locator, value, wait_time=None):
    """Allow to scroll into an element with dynamic locator using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        value (str | list) values to replace in the locator
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    logger.info(f"Scrolling element into view {value}")
    locator = locator[0], locator[1].format(*value)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    driver.execute_script("arguments[0].scrollIntoView();", elem)


def get_number_of_elements(self, locator, elem_name, wait_time=None):
    """Allow to get the number of elements by locator using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    try:
        elems = _driver_wait.until(EC.visibility_of_all_elements_located((locator[0], locator[1])),
                                   wait_msg.format(locator))
        logger.info(f"Got number of elements of: {elem_name} as: {len(elems)}")
    except (NoSuchElementException, TimeoutException):
        return 0
    return len(elems)


def get_number_of_elements_replace_value(self, locator, value, elem_name, wait_time=None):
    """Allow to get the number of elements by dynamic locator using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        value (str | list) values to replace in the locator
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Returns:
        (int): number of elements
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    try:
        locator = locator[0], locator[1].format(*value)
        elems = _driver_wait.until(EC.visibility_of_all_elements_located((locator[0], locator[1])),
                                   wait_msg.format(locator))
        actual_count = len(elems)
    except (NoSuchElementException, TimeoutException):
        return 0
    logger.info(f"Got number of elements of: {elem_name} with value {value} as: {len(elems)}")
    return actual_count


def get_element_text(self, locator, elem_name, wait_time=None):
    """Allow to get the text of a element using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Returns:
        (str): text of element
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    actual_text = elem.text
    logger.info(f"Text returned from element '{elem_name}' is {actual_text}")
    return actual_text


def get_element_text_replace_value(self, locator, value, elem_name, wait_time=None):
    """Allow to get the text of a element with dynamic locator using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        value (str | list) values to replace in the locator
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Returns:
        (str): text of element
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    locator = locator[0], locator[1].format(*value)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    actual_text = elem.text
    logger.info(f"Element: {elem_name} replaced with value: {value} has text: {actual_text}")
    return actual_text


def get_elements_texts_replace_value(self, locator, value, elem_name, wait_time=None):
    """Allow to get the text of multiple elements with dynamic locator using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        value (str | list) values to replace in the locator
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Returns:
        (list(str)): text of element
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    locator = locator[0], locator[1].format(*value)
    elems = _driver_wait.until(EC.visibility_of_all_elements_located((locator[0], locator[1])),
                               wait_msg.format(locator))
    texts = []
    for elem in elems:
        texts.append(elem.text)
    logger.info(f"Elements: {elem_name} replaced with value: {value} has texts: {texts}")
    return texts


def get_element_text_no_wait(self, locator, elem_name):
    """Allow to get the text of a element with no wait using selenium
    Return text of element without waiting for its visibility, useful where page is already loaded with all elements

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Returns:
        (str): text of element
    """
    _setup_wrapper(wait_for_load=True)
    elem = driver.find_element(**locator)
    text = elem.text.strip()
    logger.info(f"Text returned from element '{elem_name}' is {text}")
    return text


def get_elements_texts(self, locator, elem_name, wait_time=None):
    """Allow to get the text of multiple elements using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Returns:
        (list(str)): text of elements
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elems = _driver_wait.until(EC.visibility_of_all_elements_located((locator[0], locator[1])),
                               wait_msg.format(locator))
    texts = []
    for elem in elems:
        texts.append(elem.text.strip())
    logger.info(f"Texts returned from element '{elem_name}' is {texts}")
    return texts


def clear_input_field_entry(locator, elem_name, wait_time=None):
    """Allow to clear an input element using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    elem.clear()
    logger.info(f"Input {elem_name} has been cleared")


def click_checkbox(self, locator, value, elem_name, wait_time=None):
    """Allow to select or unselect a checkbox element using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        value (bool): value to select or unselect checkbox
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    checked_txt = ""
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    if type(value) == str:
        value = value.lower()
    if (elem.is_selected() and not value) or (not elem.is_selected() and value):
        driver.execute_script("arguments[0].click();", elem)
    else:
        checked_txt = "already "
    checked_txt += "checked" if value else "unchecked"
    logger.info(f"{elem_name} {checked_txt}")


def click_checkbox_with_replace_value(self, locator, value, selected, elem_name, wait_time=None):
    """Allow to select or unselect a checkbox element using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        selected (bool): value to select or unselect checkbox
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    locator = locator[0], locator[1].format(*value)
    checked_txt = ""
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    if type(selected) == str:
        selected = selected.lower()
    if (elem.is_selected() and not selected) or (not elem.is_selected() and selected):
        driver.execute_script("arguments[0].click();", elem)
    else:
        checked_txt = "already "
    checked_txt += "checked" if selected else "unchecked"
    logger.info(f"{elem_name} {checked_txt}")


def click_on_multiple_checkboxes(locator, elem_name, wait_time=None):
    """Allow to select multiple checkboxes elements using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elems = _driver_wait.until(EC.visibility_of_all_elements_located((locator[0], locator[1])),
                               wait_msg.format(locator))
    for elem in elems:
        driver.execute_script("arguments[0].click();", elem)
    logger.info(f"Checkboxes with name: {elem_name} checked")


def type_value(locator, text, elem_name, wait_time=None):
    """Allow to type a value on input text element using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        text (str): value to type inside input
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    elem.clear()
    elem.send_keys(text)
    if not "password" in elem_name.lower():
        logger.info(f"Entered text {text} in textbox {elem_name}")
    else:
        logger.info(f"Entered password ********** in textbox {elem_name}")


def type_value_as_human(locator, text, elem_name, typing_interval=0.25, wait_time=None):
    """Allow to type a value on input text element doing a wait between every letter type
    (simulating human typing) using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        text (str): value to type inside input
        elem_name (str): description of the element
        typing_interval (float): interval to type every letter of the text
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    elem.clear()
    for letter in text:
        elem.send_keys(letter)
        time.sleep(typing_interval)
    if not "password" in elem_name:
        logger.info(f"Entered text {text} in textbox {elem_name}")
    else:
        logger.info(f"Entered password ********** in textbox {elem_name}")


def type_value_with_keys(locator, text, elem_name, wait_time=None):
    """Allow to type a value on input text element with Control+A using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        text (str): value to type inside input
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    if current_os == "Darwin":
        elem.send_keys(Keys.COMMAND, 'A', Keys.DELETE)
    else:
        elem.send_keys(Keys.CONTROL, 'A', Keys.DELETE)
    elem.send_keys(text)
    logger.info(f"Entered text {text} in textbox {elem_name}")


def text_area_type_value(locator, text, elem_name, wait_time=None):
    """Allow to type a value in a textarea element using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        text (str): value to type inside input
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    elem.clear()
    time.sleep(0.1)
    elem.click()
    elem.send_keys(text)
    logger.info(f"Entered text {text} in textarea {elem_name}")


def type_value_with_replace_value(locator, value, text, elem_name, wait_time=None):
    """Allow to type a value on input text element with dynamic locator using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        value (str | list): values to replace in the locator
        text (str): values to type inside input
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    logger.info(f"Type Value: {text} in: {elem_name} with replace: {value}")
    locator = locator[0], locator[1].format(*value)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    elem.clear()
    time.sleep(0.1)
    elem.send_keys(text)


def type_value_with_replace_value_and_enter(self, locator, value, text, elem_name, wait_time=None):
    """Allow to type a value on input text element with dynamic locator and press enter using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        value (str | list): values to replace in the locator
        text (str): values to type inside input
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    logger.info(f"Type Value: {text} in: {elem_name} with replace: {value}")
    locator = locator[0], locator[1].format(*value)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    elem.clear()
    time.sleep(0.1)
    elem.send_keys(text + Keys.ENTER)


def type_value_and_enter(self, locator, text, elem_name, wait_time=None):
    """Allow to type a value on input text element and press enter using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        text (str): values to type inside input
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    elem.clear()
    time.sleep(0.1)
    elem.send_keys(text + Keys.ENTER)
    logger.info(f"Entered text {text} in textbox {elem_name}")


def type_value_key_down_enter(self, locator, text, elem_name, wait_time=None):
    """Allow to type a value on input text element and press keydown and enter using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        text (str): values to type inside input
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    elem.clear()
    time.sleep(0.1)
    elem.send_keys(text)
    elem.send_keys(Keys.DOWN + Keys.ENTER)
    logger.info(f"Entered text {text} in textbox {elem_name}")


def press_enter_key(self, locator, elem_name, wait_time=None):
    """Allow to press enter in an element using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    elem.send_keys(Keys.ENTER)
    logger.info(f"Pressing Enter in element {elem_name}")


def get_attribute(self, locator, attribute_name, elem_name, wait_time=None):
    """Allow to get an attribute of an element using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        attribute_name (str): css attribute name
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Returns:
        (str) attribute value
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])))
    attribute_value = elem.get_attribute(attribute_name)
    logger.info(f"Element: {elem_name} has attribute {attribute_name} with value: {attribute_value}")
    return attribute_value


def get_attribute_replace_value(self, locator, attribute_name, value, elem_name, wait_time=None):
    """Allow to get an attribute of an element with dynamic locator using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        attribute_name (str): css attribute name
        value (str | list): values to replace in the locator
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Returns:
        (str) attribute value
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    locator = locator[0], locator[1].format(*value)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])))
    attribute_value = elem.get_attribute(attribute_name)
    logger.info(
        f"Element: {elem_name} has attribute {attribute_name} with value: {attribute_value} with replace value: {value}")
    return attribute_value


def get_elements_attribute(self, locator, attribute_name, elem_name, wait_time=None):
    """Allow to get an attribute of an element using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        attribute_name (str): css attribute name
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Returns:
        (list(str)) attributes values
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elems = _driver_wait.until(EC.visibility_of_all_elements_located((locator[0], locator[1])),
                               wait_msg.format(locator))
    values = []
    for elem in elems:
        values.append(elem.get_attribute(attribute_name))
    logger.info(f"Elements: {elem_name} have attribute {attribute_name} with value: {values}")
    return values


def get_css_attribute_value(self, locator, attribute_name, elem_name, wait_time=None):
    """Allow to get a CSS attribute of an element using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        attribute_name (str): css attribute name
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Returns:
        (str) CSS attribute value
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    attribute_value = elem.value_of_css_property(attribute_name)
    logger.info(f"Element: {elem_name} has CSS attribute {attribute_name} with value: {attribute_value}")
    return attribute_value


def select_from_drop_down(self, locator, text, elem_name, wait_time=None):
    """Allow to select value on Carbon Dropdown element using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        text (str | list): values to select in dropdown
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    # Selects value from the drop-down using aria-label attribute only
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    elem.click()
    time.sleep(0.5)
    # Option xpath
    if not type(text) is list: text = [text]
    for val in text:
        option = (By.XPATH,
                  f"//li[contains(@class,'bx--dropdown-item') or contains(@class,'bx--list-box__menu-item')]/*[contains(., '{val}')]")
        elem = _driver_wait.until(EC.visibility_of_element_located(option), wait_msg.format(option))
        elem.click()
        logger.info(f"Selected {val} from dropdown {elem_name}")


def select_from_drop_down_replace_value(self, locator, value, text, elem_name, wait_time=None):
    """Allow to select value on Carbon Dropdown element with dynamic locator using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        value (str | list): values to replace in the locator
        text (str | list): values to type inside input
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    logger.info(f"Select from drop down of: {elem_name} with replace string: {value} Value: {text}")
    locator = locator[0], locator[1].format(*value)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    elem.click()
    time.sleep(0.5)
    # Option xpath
    if not type(text) is list: text = [text]
    for val in text:
        option = (By.XPATH,
                  f"//li[contains(@class,'bx--dropdown-item') or contains(@class,'bx--list-box__menu-item')]/*[contains(., '{val}')]")
        elem = _driver_wait.until(EC.visibility_of_element_located(option), wait_msg.format(option))
        elem.click()
        logger.info(f"Selected {val} from dropdown {elem_name}")


# TODO: Temp fix for EMP UI Select contexts. Need to look for a xpath fix
def select_from_context_drop_down_replace_value(locator, value, text, elem_name, wait_time=None):
    """Allow to select value on Carbon Dropdown element with dynamic locator using selenium

        Args:
            locator (tuple): tuple with locator type and locator string
            value (str | list): values to replace in the locator
            text (str | list): values to type inside input
            elem_name (str): description of the element
            wait_time (float, optional): custom wait time for the elements, skips driver default wait time
        """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    logger.info(f"Select from drop down of: {elem_name} with replace string: {value} Value: {text}")
    locator = locator[0], locator[1].format(*value)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    scroll_element_into_view((locator[0], locator[1]))
    elem.click()
    time.sleep(0.5)
    # Option xpath
    if not type(text) is list: text = [text]
    for val in text:
        option = (By.XPATH,
                  f"//div[@id='{value[0]}']//ul[contains(@class,'bx--list-box__menu') or contains(@class,'bx--dropdown-list') or contains(@class,'bx--search-dropdown')]//li/*[contains(.,'{val}')]")
        elem = _driver_wait.until(EC.visibility_of_element_located(option), wait_msg.format(option))
        elem.click()
        logger.info(f"Selected {val} from dropdown {elem_name}")


def select_from_drop_down_search_text(self, locator, value, elem_name, wait_time=None):
    """Allow to select a value on Carbon Dropdown with search using selenium (Only XPATH)

    Args:
        locator (tuple): tuple with locator type and locator string
        value (str): value to select in dropdown
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    elem.click()
    logger.info("Clicked on " + elem_name + " dropdown")
    dropdown_values = (By.XPATH, f"{locator[1]}//ul//li/button")
    values = get_elements_texts(dropdown_values, f"{elem_name} texts")
    for num, name in enumerate(values, start=1):
        if name == value:
            dropdown_value = (By.XPATH, f"({locator[1]}//ul//li/button)[{num}]")
            element = _driver_wait.until(EC.visibility_of_element_located(dropdown_value),
                                         wait_msg.format(dropdown_value))
            element.click()
            logger.info(f"Selected Value {value} from Dropdown {elem_name}")


def select_from_drop_down_search_text_with_replace_value(self, locator, value, text, elem_name, wait_time=None):
    """Allow to select a value on Carbon Dropdown with search using selenium (Only XPATH)

    Args:
        locator (tuple): tuple with locator type and locator string
        value (str | list): values to replace in the locator
        text (str): value to select in dropdown
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    locator = locator[0], locator[1].format(*value)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    elem.click()
    logger.info("Clicked on " + elem_name + " dropdown")
    dropdown_values = (By.XPATH, f"{locator[1]}//ul//li/button")
    values = get_elements_texts(dropdown_values, f"{elem_name} texts")
    for num, name in enumerate(values, start=1):
        if name == text:
            dropdown_value = (By.XPATH, f"({locator[1]}//ul//li/button)[{num}]")
            element = _driver_wait.until(EC.visibility_of_element_located(dropdown_value),
                                         wait_msg.format(dropdown_value))
            element.click()
            logger.info(f"Selected Value {text} from Dropdown {elem_name}")


def select_multiple_values_from_dropdown(self, locator, values, elem_name, wait_time=None):
    """Allow to select values on Carbon Dropdown Multiselect using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        values (list(str)): values to select in the dropdown
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    dropdown = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                                  wait_msg.format(locator))
    dropdown.click()
    logger.info(f"Clicked on {elem_name} multi-select dropdown")

    for i in values:
        # Search by the text inside the dropdown option
        elem = (By.XPATH, f"//*[contains(@id,'dropdown-option__')]/*[normalize-space()='{i}']")
        dropdownvalue = _driver_wait.until(EC.visibility_of_any_elements_located(elem),
                                           wait_msg.format(elem))
        dropdownvalue[0].click()
        logger.info(f"Selected {i} from multi-select dropdown")
    dropdown.click()


def select_multiple_values_from_dropdown_search(self, locator, values, elem_name, wait_time=None):
    """Allow to select values on Carbon Dropdown Multiselect with search using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        values (list(str)): values to select in the dropdown
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    dropdown = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                                  wait_msg.format(locator))
    dropdown.click()
    logger.info(f"Clicked on {elem_name} multi-select dropdown")

    for i in values:
        # Search by the text inside the dropdown option
        elem = (By.XPATH, f"//*[contains(@id,'dropdown-option__')]/*[normalize-space()='{i}']")
        dropdownvalue = _driver_wait.until(EC.visibility_of_any_elements_located(elem),
                                           wait_msg.format(elem))
        dropdownvalue[0].click()
        logger.info(f"Selected {i} from multi-select dropdown")
    elem1 = (By.CSS_SELECTOR, f"#{locator[1]}  .bx--tag--filter")
    selected_value = _driver_wait.until(EC.visibility_of_any_elements_located(elem1),
                                        wait_msg.format(elem1))
    selected_value[0].click()
    logger.info("Closed dropdown values list")


def select_option_from_dropdown_list(self, locator, value, elem_name, wait_time=None):
    """Allow to select a value on Carbon Dropdown List using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        value (str): value to select in dropdown
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    elem.click()
    logger.info(f"Clicked on {elem_name} dropdown")

    dropdown_values = (By.XPATH, "//ibm-dropdown-list//li")
    values = get_elements_texts(dropdown_values, f"{elem_name} texts")
    for num, name in enumerate(values, start=1):
        if name == value:
            dropdown_value = (By.XPATH, f"(//ibm-dropdown-list//li)[{num}]")
            element = _driver_wait.until(EC.visibility_of_element_located(dropdown_value),
                                         wait_msg.format(dropdown_value))
            element.click()
            logger.info(f"Selected Value {value} from Dropdown {elem_name}")
            break


def text_input_search(self, locator, value, elem_name, wait_time=None):
    """Allow to select a value on Carbon Text Input Search using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        value (str): value to select in dropdown
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    input = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                               wait_msg.format(locator))
    logger.info(f"Search {value} on {elem_name}")
    input.send_keys(value)
    option_locator = f"//button//span[contains(text(), '{value}') or *[contains(text(), '{value}')]]/.."
    option = _driver_wait.until(EC.visibility_of_any_elements_located((By.XPATH, option_locator)),
                                wait_msg.format(option_locator))
    option[0].click()
    logger.info(f"Selected value: {value} on {elem_name}")


def blur_element_using_js(self, locator, elem_name, wait_time=None):
    """Allow to remove the focus from an element with javascript using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                       wait_msg.format(locator))
    driver.execute_script("document.activeElement.blur();", None)
    logger.info(f"Blur element  {elem_name}")


def wait_for_all_elements_to_load(self, locator, elem_name, wait_time=None):
    """Allow to wait until all elements load using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    logger.info(f"Wait for all child elements to load: {elem_name}")
    _driver_wait.until(EC.presence_of_all_elements_located((locator[0], locator[1])),
                       wait_msg.format(locator))


def wait_for_all_elements_to_load_replace_value(self, locator, value, elem_name, wait_time=None):
    """Allow to wait until all elements load with dynamic locator using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        value (str | list): values to replace in the locator
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    logger.info(f"Wait for all child elements to load: {elem_name} with replace text: {value}")
    locator = locator[0], locator[1].format(*value)
    _driver_wait.until(EC.presence_of_all_elements_located((locator[0], locator[1])),
                       wait_msg.format(locator))


def wait_for_element_to_visible(self, locator, elem_name, wait_time=None):
    """Allow to wait until an element is visible using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    logger.info(f"Wait for {elem_name} to be visible")
    _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                       wait_msg.format(locator))
    logger.info(f"Element: {elem_name} is visible")


def wait_for_element_to_visible_with_replace_value(self, locator, value, elem_name, wait_time=None):
    """Allow to wait until an element is visible with dynamic locator using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        value (str | list): values to replace in the locator
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    locator = locator[0], locator[1].format(*value)
    _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                       wait_msg.format(locator))
    logger.info(f"Wait for element visible : {elem_name} with replace text: {value}")


def wait_for_element_to_invisible(self, locator, elem_name, wait_time=None):
    """Allow to wait until an element is invisible using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    logger.info(f"Wait for {elem_name} to be invisible")
    _driver_wait.until(EC.invisibility_of_element_located((locator[0], locator[1])),
                       wait_msg.format(locator))
    logger.info(f"Element: {elem_name} is invisible")


def wait_for_element_to_invisible_with_replace_value(self, locator, value, elem_name, wait_time=None):
    """Allow to wait until an element is invisible with dynamic locator using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        value (str | list): values to replace in the locator
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    locator = locator[0], locator[1].format(*value)
    _driver_wait.until(EC.invisibility_of_element_located((locator[0], locator[1])),
                       wait_msg.format(locator))
    logger.info(f"Wait for element visible : {elem_name} with replace text: {value}")


def wait_for_element_clickable(self, locator, value, wait_time=None):
    """Allow to wait until an element is clickable using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    _driver_wait.until(EC.element_to_be_clickable((locator[0], locator[1])), wait_msg.format(locator))
    logger.info(f"Waiting for {value} to be clickable")


def wait_for_element_text(self, locator, text, elem_name, wait_time=None):
    """Allow to wait until an element has a text present using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        text (str): text to wait to be present in element
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    logger.info(f'Waiting for text: {text} in element: {elem_name}')
    _driver_wait.until(EC.text_to_be_present_in_element((locator[0], locator[1]), text),
                       wait_msg.format(locator))


def wait_for_element_text_with_replace_value(self, locator, value, text, elem_name, wait_time=None):
    """Allow to wait until an element has a text present with dynamic locator using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        value (str | list): values to replace in the locator
        text (str): text to wait to be present in element
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    logger.info(f'Waiting for text: {text} in element: {elem_name}')
    locator = locator[0], locator[1].format(*value)
    _driver_wait.until(EC.text_to_be_present_in_element((locator[0], locator[1]), text),
                       wait_msg.format(locator))


def get_canvas_image(self, locator, elem_name, wait_time=None):
    """Allow to get the canva in base64 from an element using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Returns:
        (str) PNG in base64 string
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    # get the canvas as a PNG base64 string
    canvas_image = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", elem)
    logger.info(f"Got Canvas for element: {elem_name}")
    return canvas_image


def switch_to_new_window(self, window_num):
    """Allow to switch to a window tab using selenium
    Args:
        window_num (int): tab number
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    tabs = driver.window_handles
    driver.switch_to.window(tabs[window_num])
    logger.info(f"Switching to window number {window_num}")


def switch_to_parent_window(self):
    """Allow to switch to the parent window tab using selenium
    Args:
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    # Close window where driver is set and then switch back to parent window
    driver.close()
    tabs = driver.window_handles
    driver.switch_to.window(tabs[0])
    logger.info("Switching to parent tab")


"""
------------------------------------------------------------------------
Elements Validations    
------------------------------------------------------------------------
"""


def is_element_present(locator, elem_name, stop_on_fail=False, wait_time=None):
    """Allow to verify if an element is present using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        stop_on_fail (bool, optional): Allow to raise the exception if element is not found. Defaults to False.
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Raises:
        ex: selenium exception if stop_on_fail equal to True

    Returns:
        bool: element is found or not
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    try:
        _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                           wait_msg.format(locator))
    except (NoSuchElementException, TimeoutException) as ex:
        logger.info(f"Element {elem_name} is not present")
        if stop_on_fail:
            raise ex
        return False
    logger.info(f"Element {elem_name} is present")
    return True


def is_element_not_present(self, locator, elem_name, stop_on_fail=False, wait_time=None):
    """Allow to verify if an element is not present using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        stop_on_fail (bool, optional): Allow to raise the exception if element is not found. Defaults to False.
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time


    Raises:
        ex: selenium exception if stop_on_fail equal to True

    Returns:
        bool: element is found or not
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    try:
        _driver_wait.until(EC.invisibility_of_element_located((locator[0], locator[1])),
                           wait_msg.format(locator))
    except (NoSuchElementException, TimeoutException) as ex:
        logger.info(f"Element {elem_name} is present")
        if stop_on_fail:
            raise ex
        return False
    logger.info(f"Element {elem_name} is not present")
    return True


def is_element_present_replace_value(locator, value, elem_name, stop_on_fail=False, wait_time=None):
    """Allow to verify if an element is present with dynamic locator using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        value (str | list) values to replace in the locator
        elem_name (str): description of the element
        stop_on_fail (bool, optional): Allow to raise the exception if element is not found. Defaults to False.
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Raises:
        ex: selenium exception if stop_on_fail equal to True

    Returns:
        bool: element is found or not
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if not type(value) is list: value = [value]
    logger.info(f"Checking element '{elem_name}' with value: '{value}' is present")
    try:
        locator = locator[0], locator[1].format(*value)
        _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                           wait_msg.format(locator))
    except (NoSuchElementException, TimeoutException) as ex:
        logger.info(f"Element '{elem_name}' with value: '{value}' is not present")
        if stop_on_fail:
            raise ex
        return False
    logger.info(f"Element '{elem_name}' with value: '{value}' is present")
    return True


def check_element_exists(locator, wait_time=None):
    """Allow to verify if an element is present with dynamic locator using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Returns:
        bool: element is found or not
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    try:
        driver.find_element(locator[0], locator[1])
    except NoSuchElementException:
        return False
    return True


def is_element_enable(locator, elem_name, wait_time=None):
    """Allow to verify if an element is enabled using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Returns:
        bool: element is enabled or not
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    try:
        elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                                  wait_msg.format(locator))
        ele_status = elem.is_enabled()
        if ele_status:
            logger.info(f"Element {elem_name} is present and enabled")
        else:
            logger.info(f"Element {elem_name} is present but disabled")
        return ele_status
    except (NoSuchElementException, TimeoutException):
        logger.info(f"Element {elem_name} is not present on the page")
        return False


def is_checkbox_checked(locator, elem_name, replace_value=list(), wait_time=None):
    """Allow to verify if a checkbox is checked using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        replace_value (str | list) element to replace in the locator
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Returns:
        bool: element is checked or not
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    if type(replace_value) != list: replace_value = [replace_value]
    elem = _driver_wait.until(
        EC.visibility_of_element_located((locator[0], locator[1].format(*replace_value))),
        wait_msg.format(locator))
    checked = elem.is_selected()
    if checked:
        logger.info(f'Element {elem_name} is checked')
    else:
        logger.info(f'Element {elem_name} is not checked')
    return checked


def is_element_clickable(locator, elem_name, stop_on_fail=False, wait_time=None):
    """Allow to verify if an element is clickable using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        stop_on_fail (bool, optional): Allow to raise the exception if element is not found. Defaults to False.
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Raises:
        ex: selenium exception if stop_on_fail equal to True

    Returns:
        bool: element is found or not
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    try:
        _driver_wait.until(EC.element_to_be_clickable((locator[0], locator[1])), wait_msg.format(locator))
    except (NoSuchElementException, TimeoutException) as ex:
        logger.info(f"Element {elem_name} is not present")
        if stop_on_fail:
            raise ex
        return False
    logger.info(f"Element {elem_name} is present and Clickable")
    return True


def are_elements_present_by_replace_value(locator, values, base_elem_name, stop_on_fail=False,
                                          wait_time=None):
    """Allow to verify if multiple elements are present with dynamic locator using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        values (str | list) values to replace in the locator
        base_elem_name (str): description of the base element
        stop_on_fail (bool, optional): Allow to raise the exception if element is not found. Defaults to False.
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Raises:
        ex: selenium exception if stop_on_fail equal to True

    Returns:
        bool: element is found or not
    """
    if not type(values) is list: raise f"Argument 'values' is not a list"
    logger.info(f"Checking elements '{values}' with locator: '{locator}' are present")
    for value in values:
        is_element_present_replace_value(locator, value, base_elem_name.format(value), stop_on_fail,
                                         wait_time=wait_time)


"""
------------------------------------------------------------------------
Page Operations
------------------------------------------------------------------------
"""


def upload_file(locator, file_path, wait_time=None):
    """Allow to upload a file using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        file_path (str): string with file path
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    logger.info("Trying to Upload to path: {0}  >> file:{1}".format(locator, file_path))
    elem = _driver_wait.until(EC.presence_of_element_located((locator[0], locator[1])),
                              wait_msg.format(locator))
    driver.execute_script(
        'arguments[0].style = ""; arguments[0].style.display = "block"; arguments[0].style.visibility = "visible";',
        elem)
    elem.send_keys(file_path)


def refresh_current_page():
    """Allow to refresh the current page using selenium
    """
    _setup_wrapper()
    driver.refresh()


def send_arrow_down_key(locator, elem_name, wait_time=None):
    """Allow to send a down arrow key to the element

    Args:
        locator (tuple): tuple with locator type and locator string
        elem_name (str): description of the element
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    elem = _driver_wait.until(EC.visibility_of_element_located((locator[0], locator[1])),
                             wait_msg.format(locator))
    elem.send_keys(Keys.ARROW_DOWN)
    logger.info(f"Arrow down was pressed on {elem_name}")


def switch_to_iframe(locator, wait_time=None):
    """Allow to switch to an iframe using selenium

    Args:
        locator (tuple): tuple with locator type and locator string
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    logger.info(f"Switch to iframe with locator: {locator[1]}")
    _driver_wait.until(EC.frame_to_be_available_and_switch_to_it((locator[0], locator[1])),
                       wait_msg.format(locator))


def switch_to_parent_iframe(wait_time=None):
    """Allow to switch to the parent iframe of the current iframe using selenium

    Args:
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    logger.info("Switch to parent iframe")
    driver.switch_to.parent_frame()


def switch_to_default_content_iframe(wait_time=None):
    """Allow to switch to the default content of the page using selenium

    Args:
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    logger.info("Switch to default content iframe")
    driver.switch_to.default_content()


def wait_for_spinner_off(locator=(By.CSS_SELECTOR, ".bx--loading__svg"), stop_on_fail=True, wait_time=None):
    """Allow to wait for the page loader spinner to disappear using selenium
    Args:
        locator (tuple, optional):  tuple with locator type and locator string. Defaults to (By.CSS_SELECTOR, ".bx--loading__svg").
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Returns:
        bool: returns if loader is present or not
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    try:
        _driver_wait.until(EC.invisibility_of_element_located(locator), wait_msg.format(locator))
        logger.info("Spinner is off")
        return True
    except TimeoutException as ex:
        logger.info("Spinner is not disappeared after time limit")
        if stop_on_fail:
            raise ex
        return False


def wait_for_spinner_on(locator=(By.CSS_SELECTOR, ".bx--loading__svg"), stop_on_fail=True, wait_time=None):
    """Allow to wait for the page loader spinner to appear using selenium
    Args:
        locator (tuple, optional):  tuple with locator type and locator string. Defaults to (By.CSS_SELECTOR, ".bx--loading__svg").
        wait_time (float, optional): custom wait time for the elements, skips driver default wait time

    Returns:
        bool: returns if loader is present or not
    """
    _setup_wrapper(wait_time, wait_for_load=True)
    try:
        _driver_wait.until(EC.visibility_of_element_located(locator), wait_msg.format(locator))
        logger.info("Spinner is on")
        return True
    except TimeoutException as ex:
        logger.info("Spinner is not appeared after time limit")
        if stop_on_fail:
            raise ex
        return False
