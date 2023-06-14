"""Web crawler using selenium"""

from __future__ import annotations

from pathlib import Path
from sys import platform

from bs4 import BeautifulSoup
from requests.compat import urljoin
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from typing import Any

FILE_DIR = None
CFG = None
from plughcontrol.commands.command import command


@command("get html info", "get html info", '"url": "<url>"')
# 爬取指定URL下的所有内容，并返回文本摘要（未完成）和链接列表（未完成）
def scrape_all(url: str) -> Any:
    print('爬取页面')
    print(url)
    try:
        driver, text = get_text(url[1:-1])
    except WebDriverException as e:
        error_msg = e.msg.split("\n")[0]
        return f"Error: {error_msg}"
    print(text)

    print("\n提取链接中……（尚未完成）\n")

    # links = get_links(driver, url)
    # print(links)

    driver.close()
    return text[100:10000]


# 访问指定URL，获取其前端文本内容并进行处理，返回浏览器驱动实例和纯文本内容
def get_text(url: str) -> tuple[WebDriver, str]:
    options = Options()
    # options.headless = True
    options.add_argument("--disable-gpu")
    driver = webdriver.Edge(options=options)
    driver.get(url)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    page_source = driver.execute_script("return document.body.outerHTML;")
    soup = BeautifulSoup(page_source, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = "\n".join(chunk for chunk in chunks if chunk)
    return driver, text


def get_links(driver: WebDriver, url: str) -> list[str]:
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    hyperlinks = extract_hyperlinks(soup, url)

    # 从BS对象中提取全部链接，返回一个链接列表，其中每个链接以(文本, URL)的形式储存


def extract_hyperlinks(soup: BeautifulSoup, base_url: str) -> list[tuple[str, str]]:
    """Extract hyperlinks from a BeautifulSoup object

    Args:
        soup (BeautifulSoup): The BeautifulSoup object
        base_url (str): The base URL

    Returns:
        List[Tuple[str, str]]: The extracted hyperlinks
    """
    return [
        (link.text, urljoin(base_url, link["href"]))
        for link in soup.find_all("a", href=True)
    ]


def format_hyperlinks(hyperlinks: list[tuple[str, str]]) -> list[str]:  # 将上一函数返回的（以元组为元素的）列表格式化为以“链接文本(URL)”为元素的列表并返回
    """Format hyperlinks to be displayed to the user

    Args:
        hyperlinks (List[Tuple[str, str]]): The hyperlinks to format

    Returns:
        List[str]: The formatted hyperlinks
    """
    return [f"{link_text} ({link_url})" for link_text, link_url in hyperlinks]


if __name__ == '__main__':
    # url = input()
    print(scrape_all("http://www.weather.com.cn/weather/101270101.shtml"))
