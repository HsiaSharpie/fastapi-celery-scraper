from celery import shared_task

from project import config, models, database
from project.news.utils import get_lastest_news, store_news_content, email_notification, check_rapper_consists

sender_email = config.settings.SENDER_EMAIL
sender_password = config.settings.SENDER_PASSWORD
receiver_email = config.settings.RECEIVER_EMAIL


@shared_task
def crawl_url():
    # crawl news
    query_term_list = ["쿠기", "애쉬 아일랜드"]
    insert_news_list = []

    for query_term in query_term_list:
        # check rapper consists
        rappper_query_result = check_rapper_consists(query_term)
        if not rappper_query_result:
            session = database.SessionLocal()
            rapper_object = models.Rapper(rap_name=query_term)
            session.add(rapper_object)
            session.commit()
            session.refresh(rapper_object)

        # crawl news from naver
        news_data_list = get_lastest_news(query_term)
        if not news_data_list:
            return False

        # insert news metadata to postgresql
        insert_news = store_news_content(news_data_list)
        insert_news_list.extend(insert_news)

    # email notification
    if len(insert_news_list) != 0:
        email_status = email_notification(insert_news_list, sender_email,
                                          sender_password, receiver_email)
        return email_status
    return True
