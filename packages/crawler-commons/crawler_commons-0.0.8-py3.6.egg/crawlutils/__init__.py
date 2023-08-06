from datetime import datetime
import requests

class Interval:
    def __init__(self, level: int, fr: str, to: str, secs: int):
        self.level = level
        self.time_from = None if len(fr) < 1 else datetime.strptime(fr, "%H:%M").time()
        self.time_to = None if len(to) < 1 else datetime.strptime(to, "%H:%M").time()
        self.secs = secs

    def __str__(self):
        return f"level : {self.level}, from : {self.time_from}, to : {self.time_to}, secs : {self.time_to}"


class CrawlingInterval:
    """
    설정에 따라 crawling interval 을 설정한다
    """
    def __init__(self, intervals):
        self.intervals = list(map(lambda x: Interval(x.get("level"), x.get("from"), x.get("to"), x.get("secs")), intervals))

    def choose_sleep_time(self, dt):
        t = dt.time()
        default_secs = 10
        for interval in self.intervals:
            if interval.time_from is None:
                default_secs = interval.secs
            else:
                if interval.time_from <= t < interval.time_to:
                    return interval.secs

        return default_secs

def get_public_ip():
    headers = {
        'authority': 'icanhazip.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,ko;q=0.8',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    }

    response = requests.get('https://icanhazip.com/', headers=headers)
    return response.text.strip()


if __name__ == "__main__":
    # c = CrawlingInterval()
    # assert(0.4 == c.choose_sleep_time(datetime(1970, 1, 1, 10, 10)))
    # assert(1 == c.choose_sleep_time(datetime(1970, 1, 1, 16, 10)))
    # assert(1 == c.choose_sleep_time(datetime(1970, 1, 1, 8, 59)))
    # assert(0.4 == c.choose_sleep_time(datetime(1970, 1, 1, 15, 59)))
    # assert(0.4 == c.choose_sleep_time(datetime(1970, 1, 1, 9, 0)))
    #
    ip = get_public_ip()
    print(f"public ip : [{ip}]")