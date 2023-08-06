Simple Request class 


## Usage

``` python

from bw_requests import Requests
service=Requests('https://www.libero.it').get('',headers={"Content-Type": 'application/json; charset=UTF-8','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'})

print(service)

service=Requests('https://www.libero.it').get('',headers={"Content-Type": 'application/json; charset=UTF-8'})

print(service)

```

