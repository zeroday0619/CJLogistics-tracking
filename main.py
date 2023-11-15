import ujson
import httpx
from scrapy import Selector
from fake_useragent import UserAgent

class HTTPEXceptions(Exception):
    def __init__(self, status: int, message: str) -> None:
        self.status = status
        self.message = message
    
    def __str__(self) -> str:
        return f'HTTP {self.status} {self.message}'

class NoCsrfException(Exception):
    pass

class CJLogistics(object):
    def __init__(self) -> None:
        self.tracking_page_url = "https://www.cjlogistics.com/ko/tool/parcel/tracking"
        self.tracking_url = "https://www.cjlogistics.com/ko/tool/parcel/tracking-detail"
        self.user_agent = UserAgent()
        self.client = httpx.Client(
            headers={
                "User-Agent": self.user_agent.random
            }
        )
    
    @staticmethod
    def check_status(status) -> None:
        match status:
            case 200:
                pass
            case 404:
                raise HTTPEXceptions(404, "Not Found")
            case 500:
                raise HTTPEXceptions(500, "Internal Server Error")
            case _:
                raise HTTPEXceptions(status, "Unknown Error")

    def get_cerf_key(self) -> str:
        response = self.client.get(self.tracking_page_url)
        self.check_status(response.status_code)
        html = response.text
        soup = Selector(text=html)
        _input = soup.xpath('//*[@id="frmUnifiedSearch"]/input')
        _csrf = _input.attrib.get("value")
        if not _csrf:
            raise NoCsrfException("No CSRF token")
        return _csrf
    
    def get_tracking(self, tracking_number: str) -> str:
        response = self.client.post(
            url=self.tracking_url,
            data={
                "_csrf": self.get_cerf_key(),
                "paramInvcNo": tracking_number
            }
        )
        self.check_status(response.status_code)
        return response.json()
    

if __name__ == "__main__":
    app = CJLogistics()
    tracking = app.get_tracking("000000000000")
    print(ujson.dumps(tracking, ensure_ascii=False, indent=4))