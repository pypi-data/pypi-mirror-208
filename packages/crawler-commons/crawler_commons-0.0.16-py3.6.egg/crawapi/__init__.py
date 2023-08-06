import logging
from typing import Dict

import requests
from bs4 import BeautifulSoup
from cache import AdtCache, MemoryCache

from crawlutils.text_utils import make_num_include_zo, make_num

logger = logging.getLogger("naverweb")

naver_url = "https://finance.naver.com/item/main.nhn"


class NaverWeb:
    def __init__(self, cache: AdtCache = None):
        if cache is None:
            cache = MemoryCache()

        self.cache: AdtCache = cache

    def get_stock_info(self, code) -> Dict[str, int]:
        """
        :param code:
        :return:
         - market_cap : 시가총액
         - current_price : 현재가
         - total_stock_count: 상장주식수
        """
        if self.cache is not None:
            result = self.cache.hget(f"marketcap_{code}")
            if result is not None and len(result.items()) > 0:
                logger.debug(f"cache hit for market_cap {code} - {result}")
                for k, v in result.items():
                    result[k] = int(v)
                return result

        cp_r = requests.get(f"{naver_url}?code={code}")
        cp_soup = BeautifulSoup(cp_r.text, 'html.parser')

        price, mc, total_stock_count = -1, 0, 0

        try:
            price = int(cp_soup.findAll('dd')[3].text.split(' ')[1].replace(',', ''))
            mc = make_num_include_zo(cp_soup.findAll('em', id='_market_sum')[0].text)
            total_stock_count = int(make_num(cp_soup.find("th", string="상장주식수").parent.find("td").text))
            logger.debug(f"total_stock_count : {total_stock_count}")
        except Exception as ex:
            logger.exception(ex)

        data = {
            "market_cap": mc,
            "current_price": price,
            "total_stock_count": total_stock_count
        }

        if mc != 0:
            self.cache.hset(f"marketcap_{code}", data )
            logger.debug(f"set cache for code {code} - {data}")

        return data

    def get_cur_price(self, code) -> int:
        d = self.get_stock_info(code=code)
        return d.get("current_price")

    def get_market_cap(self, code) -> int:
        d = self.get_stock_info(code=code)
        return d.get("market_cap")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] > %(message)s')
    naver = NaverWeb(cache=None)

    mc = naver.get_market_cap(code="000660")
    logger.info(mc)

    price = naver.get_cur_price(code="000660")
    logger.info(price)

    d = naver.get_stock_info(code="000660")
    logger.info(f"market cap : {mc}, price : {d.get('current_price')}, total_stock_count : {d.get('total_stock_count')}")