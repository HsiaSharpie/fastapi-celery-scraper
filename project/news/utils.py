from typing import List
from fastapi import HTTPException, Depends

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlencode, quote_plus
from sqlalchemy.orm import Session

from project import database, models, schemas

news_base_url = "https://search.naver.com/search.naver?where=news&sm=tab_jum&"


def get_web_content(query_term):
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }

    encoded_query = urlencode({"query": f"{query_term}"}, quote_via=quote_plus)
    crawl_url = news_base_url + encoded_query

    resp = requests.get(crawl_url, headers=headers)
    if resp.status_code != 200:
        raise HTTPException(status_code=404, detail="Crawling Url Error")
    return resp.content


def get_lastest_news(query_term):
    content = get_web_content(query_term)
    soup = BeautifulSoup(content, "html.parser")

    # get news lists
    web_news_list = soup.find("div", class_="group_news").find(
        "ul", class_="list_news").find_all("li", class_="bx")

    news_data_list = []
    for news in web_news_list:
        news_area = news.find("div", class_="news_area")

        news_info = news_area.find("div", class_="info_group")
        source = news_info.find("a").text
        try:
            post_time = datetime.strptime(
                news_info.find("span", class_="info").text.replace(".", ""),
                "%Y%m%d")
        except:
            post_time = None

        origin_url = news_area.find("a", class_="news_tit")["href"]
        title = news_area.find("a", class_="news_tit").text

        news_data_list.append({
            'source': source,
            'post_time': post_time,
            'origin_url': origin_url,
            'title': title,
        })

    return news_data_list


def store_news_content(insert_news_content=List[schemas.News],
                       db: Session = Depends(database.get_db)):

    objects = [
        models.News(source=["source"],
                    post_time=news["post_time"],
                    origin_url=news["origin_url"],
                    title=news["title"]) for news in insert_news_content
    ]
    db.bulk_save_objects(objects)
    db.commit()
    db.refresh(objects)

    return True
