from celery import shared_task

from project.news.utils import get_lastest_news, store_news_content


# a = "쿠기"
@shared_task
def crawl_url():
    query_term = "쿠기"
    query_result = get_lastest_news(query_term)

    if query_result is None:
        return False

    insert_result = store_news_content(query_result)

    return insert_result