import smtplib, ssl, requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlencode, quote_plus
from typing import List
from fastapi import HTTPException

from project import database, models, schemas

news_base_url = "https://search.naver.com/search.naver?where=news&sm=tab_jum&"


def check_rapper_consists(query_term):
    session = database.SessionLocal()
    return session.query(
        models.Rapper).filter(models.Rapper.rap_name == query_term).first()


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
        post_time = news_info.find("span", class_="info").text.replace(".", "")
        origin_url = news_area.find("a", class_="news_tit")["href"]
        title = news_area.find("a", class_="news_tit").text

        # get rapper_id
        session = database.SessionLocal()
        rapper_result = session.query(models.Rapper).filter(
            models.Rapper.rap_name == query_term).first()

        news_data_list.append({
            "rapper": f"{query_term}",
            "source": source,
            "post_time": post_time,
            "origin_url": origin_url,
            "title": title,
            "related_rapper_id": rapper_result.__dict__["id"]
        })

    return news_data_list


def store_news_content(insert_news_content=List[schemas.News]):
    session = database.SessionLocal()

    insert_news_list = []
    for news in insert_news_content:
        query_result = session.query(models.News).filter(
            models.News.origin_url == news["origin_url"]).first()

        if query_result:
            continue
        news_object = models.News(rapper=news["rapper"],
                                  source=news["source"],
                                  post_time=news["post_time"],
                                  origin_url=news["origin_url"],
                                  title=news["title"],
                                  related_rapper_id=news["related_rapper_id"])
        session.add(news_object)
        session.commit()
        session.refresh(news_object)
        insert_news_list.append(news)

    return insert_news_list


def email_notification(insert_news_list, sender_email, sender_password,
                       receiver_email):

    def format_html_content(news):
        html_base = f'''
            <tr> \
                <td>{news['rapper']}</td> \
                <td>{news['source']}</td> \
                <td>{news['post_time']}</td> \
                <td>{news['origin_url']}</td> \
                <td>{news['title']}</td> \
            </tr> \
        '''
        return html_base

    html_content = " ".join(
        [format_html_content(news) for news in insert_news_list])

    # Email Metadata
    message = MIMEMultipart("alternative")
    message[
        "Subject"] = "Your Favoriate Korean HipHop Rapper's news notification"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    text = """
        Your Favoriate Korean HipHop Rapper"s news notification
    """
    html = f"""
    <html>
        <body>
            <table style="border:3px #cccccc solid;" cellpadding="10" border="1"> \
                <tr> \
                    <th>Rapper</th> \
                    <th>Source</th> \
                    <th>Post Time</th> \
                    <th>Origin Url</th> \
                    <th>Title</th> \
                </tr> \
                {html_content}
            </table>
        </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        try:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Sending email successfully.")

            return True
        except Exception as e:
            print("Error sending email.")

            return False
