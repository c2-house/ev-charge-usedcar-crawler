import json
import re
import time
import pandas as pd
from datetime import datetime
from pytz import timezone
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from driver import chrome


class EVCar:
    def __init__(self, driver, models):
        self.driver = driver
        self.models = models
        self.driver.maximize_window()

    def search(self, url):
        self.driver.get(url)
        time.sleep(5)
        page_source = BeautifulSoup(self.driver.page_source, "html.parser")
        return page_source

    def get_car_list(self, page_source):
        source = page_source.find(
            "div", attrs={"class": "common-sub-content fix-content"}
        ).find(
            "div", attrs={"class": "cs-list02 cs-list02--ratio small-tp generalRegist"}
        )
        source = source.find("div", attrs={"class": "list-in"}).find_all(
            "div", attrs={"class": "area"}
        )
        return source

    def click_price_sort(self):
        self.driver.find_element(By.ID, "sort-sellAmt").click()
        time.sleep(2)

    def get_price_list(self, page_source):
        price_list = []
        for src in page_source:
            price = src.find("strong", attrs={"class": "pay"}).text.strip()
            price = price.split(" ")
            price_list.append(price[0])
        return price_list

    def get_min_max_price(self, price_list):
        converted_prices = []
        for price in price_list:
            # 정규표현식을 사용하여 숫자만 추출
            numbers_only = re.findall(r"\d+", price.replace(",", ""))
            if numbers_only:
                # 숫자를 정수로 변환
                converted_price = int("".join(numbers_only))
                converted_prices.append(converted_price)

        sorted_prices = sorted(converted_prices)
        return sorted_prices[0], sorted_prices[-1]


with open("ev-cars.json", "r") as f:
    ev_car_dict = json.load(f)


def main():
    total = []
    driver = chrome.driver
    ev = EVCar(driver, ev_car_dict)
    for model, url in ev.models.items():
        time.sleep(3)
        page_source = ev.search(url)
        # 최저가 기준 정렬
        ev.click_price_sort()
        car_list_by_min = ev.get_car_list(page_source)
        # 최고가 기준 정렬
        ev.click_price_sort()
        car_list_by_max = ev.get_car_list(page_source)
        price_list_by_min = ev.get_price_list(car_list_by_min)
        price_list_by_max = ev.get_price_list(car_list_by_max)
        total_price_list = price_list_by_min + price_list_by_max
        min_price, max_price = ev.get_min_max_price(total_price_list)
        model, image = model.split(",")
        item = {
            "name": model,
            "min_price": min_price,
            "max_price": max_price,
            "created_at": datetime.now(timezone("Asia/Seoul")).isoformat(),
            "image": image,
        }
        total.append(item)
        print(f"{model}의 최저가는 {min_price}만원, 최고가는 {max_price}만원 입니다.")

    df = pd.DataFrame(total)
    df.to_csv("result.csv", index=False, encoding="utf-8-sig")
    driver.close()
    driver.quit()


if __name__ == "__main__":
    main()
