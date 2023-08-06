'''

w = Requests("https://api.github.com")
r = w.get("/gists/96b655f1512d1ce9d570e008dbe122d3")
print(r.json())


w = Requests("https://s5.sir.sportradar.com/lottomaticaonline/it/1")
r = w.get("/",  headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 RuxitSynthetic/1.0 v6864244215 t7160176795770098683 athfa3c3975 altpub cvcv=2 smf=0"})
print(r.text)

'''
import requests
from .useragent import userAgent


class Requests:
    def __init__(self, base_url, **kwargs):
        self.base_url = base_url
        self.session = requests.Session()

        for arg in kwargs:
            if isinstance(kwargs[arg], dict):
                kwargs[arg] = self.__deep_merge(getattr(self.session, arg), kwargs[arg])
            setattr(self.session, arg, kwargs[arg])

    def request(self, method, url, **kwargs):
        return self.session.request(method, self.base_url+url, **kwargs)

    def head(self, url, **kwargs):
        return self.session.head(self.base_url+url, **kwargs)

    def get(self, url, **kwargs):
        if ('headers' in kwargs):
            if not 'User-Agent' in kwargs['headers']:
                kwargs['headers']['User-Agent']=userAgent()
        else:
            kwargs['headers']={'User-Agent':userAgent()}


        return self.session.get(self.base_url+url, **kwargs)

    def post(self, url, **kwargs):
        if ('headers' in kwargs):
            if not 'User-Agent' in kwargs['headers']:
                kwargs['headers']['User-Agent']=userAgent()
        else:
            kwargs['headers']={'User-Agent':userAgent()}

        return self.session.post(self.base_url+url, **kwargs)

    def put(self, url, **kwargs):
        return self.session.put(self.base_url+url, **kwargs)

    def patch(self, url, **kwargs):
        return self.session.patch(self.base_url+url, **kwargs)

    def delete(self, url, **kwargs):
        return self.session.delete(self.base_url+url, **kwargs)

    def close(self):
        self.session.close()

    @staticmethod
    def __deep_merge(source, destination):
        for key, value in source.items():
            if isinstance(value, dict):
                node = destination.setdefault(key, {})
                Requests.__deep_merge(value, node)
            else:
                destination[key] = value
        return destination