import warnings
import os
import platform

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.microsoft import IEDriverManager
from globals import run_mode
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
import logging
from globals import browser

driver_wait = 10
current_os = platform.system()
driver = None
logger = logging.getLogger(__name__)
output_folder = os.path.join(os.getcwd(), "downloaded_files")



def create_driver(browser_type, run_mode):
    global driver
    browser_type = browser_type
    if os.environ.get("Browser"):
        browser_type = os.environ.get("Browser").lower()
    if browser_type == "firefox":
        cap = DesiredCapabilities().FIREFOX
        cap["marionette"] = True
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.set_preference("dom.disable_beforeunload", True)
        driver = webdriver.Firefox(GeckoDriverManager.install(), options=firefox_options, capabilities=cap)
    elif browser_type == "chrome":
        chrome_options = set_chrome_options()
        if run_mode == "yes":
            chrome_options.headless = True
            chrome_options.add_argument("--window-size=1920,1080")
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    elif browser_type == "ie":
        cap = DesiredCapabilities.INTERNETEXPLORER
        cap["NATIVE_EVENTS"] = False
        driver = webdriver.Ie(IEDriverManager.install(), capabilities=cap)
    elif browser_type == "edge":
        driver = webdriver.Edge(EdgeChromiumDriverManager.install())
    driver.execute_script("document.body.style.zoom='100%'")
    return driver



def create_wait(timeout=driver_wait):
    web_driver_wait = WebDriverWait(driver, timeout)
    return web_driver_wait


def capture_screenshot(image_name):
    driver.get_screenshot_as_file(image_name)


def kill_driver_instance():
    global driver
    driver.close()
    driver.quit()


def create_action_chains():
    return ActionChains(driver)


def load_url(app_url):
    logger.info(f"Driver wait time:::{driver_wait}")
    try:
        if "http" in app_url:
            driver.get(app_url)
        else:
            driver.get("https://" + app_url)
    except:
        logger.info("Loading BaseURL again..")
        if "http" in app_url:
            driver.get(app_url)
        else:
            driver.get("https://" + app_url)
    logger.info(f"Load URL: https://{app_url}")
    driver.maximize_window()


def reload_url(app_url):
    logger.info("RELOADING TO BASE PAGE: " + app_url)
    driver.get(app_url)
    driver.maximize_window()


def get_current_url():
    return driver.current_url


def set_chrome_options():
    options = webdriver.ChromeOptions()
    if current_os == "Linux":
        options.binary_location = "/usr/bin/google-chrome"
        options.add_argument('--disable-dev-shm-usage')
    # options.add_argument("--disable-blink-features")
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.50 ' \
                 'Safari/537.36 '
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument('ignore-certificate-errors')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--headless")
    preferences = {
        "profile.default_content_setting_values.automatic_downloads": 1,
        "download.default_directory": output_folder,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", preferences)
    return options


def set_firefox_preferences():
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.proxy.type", 4)
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", output_folder)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")
    profile.update_preferences()
    return profile


def delete_cookies():
    send_command = ('POST', '/session/$sessionId/chromium/send_command')
    driver.command_executor._commands['SEND_COMMAND'] = send_command
    driver.execute('SEND_COMMAND', dict(cmd='Network.clearBrowserCookies', params={}))
