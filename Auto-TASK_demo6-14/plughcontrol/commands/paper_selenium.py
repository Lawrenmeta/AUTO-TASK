
from __future__ import annotations

import os
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import re
import requests
from plughcontrol.commands.command import command
# keyword = "Security"
path = "/sucai"
@command("download paper", "DOWNLOAD PAPER BY KEYWORD", '"keyword": "<keyword>"')
def download_papers(keyword: str, paper_nums: int = 5) -> None:
    options = Options()
    options.headless = True
    options.add_argument("--disable-gpu")
    keyword = re.sub(r'\s+', '+', keyword)
    url = "https://paperswithcode.com/search?q=" + keyword
    print('开始下载')
    try:
        driver = webdriver.Edge(options=options)
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))                       # 等待网页加载完毕
        )
        for num in range(1, paper_nums + 1):
            paper_page = driver.find_element(By.XPATH, 
                                            f"/html/body/div[3]/div[2]/div[{num}]/div[2]/div/div[2]/div[2]/a[1]"
                                            ).get_attribute('href')
            driver.get(paper_page)
            pdf_page = driver.find_element(By.XPATH,
                                        "/html/body/div[3]/main/div[2]/div/div/a[1]"
                                        ).get_attribute('href')
            res = requests.get(pdf_page)
            file_path = os.path.join(path, keyword.replace('+', '-')) + '-' + str(num) + '.pdf'
            with open(file_path, 'wb+') as f:
                f.write(res.content)
            driver.back()
        driver.close()
    except WebDriverException as e:
        error_msg = e.msg.split("\n")[0]
        print(f"Error: {error_msg}")

# if __name__ == '__main__':
#     download_papers("Security", 2)
#