
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class ChromeDriver:
    def __init__(self) -> None:
        self.chrome_service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.chrome_service)
        
    def open(self):
        self.driver.get("https://www.kbchachacha.com/public/search/main.kbc")
        self.driver.maximize_window()
        self.driver.implicitly_wait(3)

    def close(self):
        self.driver.close()
        self.driver.quit()


chrome = ChromeDriver()