import logging
import time
import requests


def url2html(session: requests.Session, url: str, **kwargs):
  """
    Usage::

      print(url2html(requests.Session(), 'https://www.baidu.com'))

    :param timeout: default = 30
    :param max_try: default = 3
    :param retry_gap: default = 5
  """
  max_try = kwargs['max_try'] if 'max_try' in kwargs else 3
  timeout = kwargs['timeout'] if 'timeout' in kwargs else 30
  retry_gap = kwargs['retry_gap'] if 'retry_gap' in kwargs else 5

  try_cnt = 0
  result = ""

  while try_cnt < max_try:
    try:
      result = session.get(url, timeout=timeout).content.decode()
      break
    except Exception as e:
      logging.exception(e)
      try_cnt += 1
      time.sleep(retry_gap)
  return result


def html2soup(html):
  from bs4 import BeautifulSoup
  return BeautifulSoup(html, 'lxml')


def url2soup(session: requests.Session, url: str, **kwargs):
  return html2soup(url2html(session=session, url=url, **kwargs))
