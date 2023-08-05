import unittest
import json
from selenium import webdriver
from appium import webdriver as AppiumWebdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# import Faker

default_hub_host = 'selenium-hub:4444'


def get_driver(browser, hub_host):
    if (browser == 'chrome'):
        options = webdriver.ChromeOptions()
        options.add_argument('window-size=1920x1080')
        options.add_argument('ignore-certificate-errors')
        options.add_argument("incognito")
        options.add_argument("start-maximized")
        capabilities = DesiredCapabilities.CHROME.copy()
        driver = webdriver.Remote(
            command_executor="http://%s/wd/hub" % (hub_host),
            desired_capabilities=capabilities,
            options=options
        )

        return driver

    if (browser == 'firefox'):
        options = webdriver.FirefoxOptions()
        options.add_argument('-width=1920')
        options.add_argument('-height=1080')
        options.set_preference("geo.prompt.testing", True)
        options.set_preference("geo.prompt.testing.allow", False)
        capabilities = DesiredCapabilities.FIREFOX.copy()

        driver = webdriver.Remote(
            command_executor="http://%s/wd/hub" % (hub_host),
            desired_capabilities=capabilities,
            options=options
        )

        return driver

    if (browser == 'android'):
        desired_caps = dict(
            platformName='Android',
            # platformVersion='10',
            automationName='uiautomator2',
            deviceName='Android Emulator',
        )

        driver = webdriver.Remote(
            "http://%s/wd/hub" % (hub_host),
            desired_caps
        )

        return driver

    raise ValueError('Browser not supported')


def get_hub_host(config):
    if 'hub_host' in config and config['hub_host'] is not None:
        return config['hub_host']

    return default_hub_host


class BaseTestCase(unittest.TestCase):
    def __init__(self, testname, config, environment, browser):
        super(BaseTestCase, self).__init__(testname)
        BaseTestCase.environment = environment
        BaseTestCase.config = config[environment]
        BaseTestCase.browser = browser

    @classmethod
    def setUpClass(cls):
        hub_host = get_hub_host(cls.config)
        cls.driver = get_driver(cls.browser, hub_host)

        # cls.faker = Faker(['es_MX', 'en_US'])

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.reset()
        self.driver.get(self.config['url'])

    def takeScreenshot(self, test_name):
        print(self.__class__.__name__)

    #     self.driver.get_screenshot_as_file();

    def generateExceptionReport(self, exception):
        driver = self.driver
        screenshot = driver.get_screenshot_as_base64()
        console_log = driver.get_log('browser')
        console_log_string = json.dumps(console_log)
        formatedException = '''
        <p class="lead">{0}</p>
        
        <h4>Browser Screenshot</h4>
        <img src="data:image/png;base64,{1}">
        
        <h5>Browser Console</h5>
        <code>{2}</code>
        '''.format(exception, screenshot, console_log_string)

        self.reset()
        return formatedException

    def generateException(self, exception):
        driver = self.driver
        screenshot = driver.get_screenshot_as_base64()
        console_log = driver.get_log('browser')
        console_log_string = json.dumps(console_log)

        exception.browser_screenshot = screenshot
        exception.browser_console_log = console_log_string

        return exception

    def reset(self):
        # Function to click edit address checkbox
        driver = self.driver
        driver.delete_all_cookies()
        driver.refresh()

