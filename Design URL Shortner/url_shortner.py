
import string
from threading import Lock

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
# app = FastAPI()

class URLShortner:

    def __init__(self):
        self.url_db = {} # long to short url
        self.reverse_db = {} # short to long url
        self.counter = 1 # id of the short URL
        self.alphabet = string.ascii_letters + string.digits

    def encode(self,num):
        if num == 0:
            return self.alphabet[0]
        
        s = []
        base = len(self.alphabet)
        print(self.alphabet)
        while num > 0:
            s.append(self.alphabet[num % base])
            num //= base

        return ''.join(reversed(s))

    def shorten(self,long_url):

        if long_url in self.reverse_db:
            return self.reverse_db[long_url]
        
        short_url = self.encode(self.counter)
        self.url_db[short_url] = long_url
        self.reverse_db[long_url] = short_url
        self.counter += 1
        return short_url
    
    def retrieve(self, short_url):
        if short_url not in self.url_db:
            return None

        return self.url_db[short_url]
    
shortener = URLShortner()
app = FastAPI(title="In-Memory URL Shortener")


class ShortenRequest(BaseModel):
    url: HttpUrl


class ShortenResponse(BaseModel):
    original_url: str
    short_code: str
    short_url: str


@app.get("/")
def home():
    return {"message": "URL Shortener is running"}


@app.post("/api/shorten", response_model=ShortenResponse)
def shorten_url(request: ShortenRequest):
    long_url = str(request.url)
    short_code = shortener.shorten(long_url)

    return ShortenResponse(
        original_url=long_url,
        short_code=short_code,
        short_url=f"{PUBLIC_BASE_URL}/{short_code}",
    )


@app.get("/{short_code}")
def redirect_url(short_code: str):
    long_url = shortener.retrieve(short_code)

    if long_url is None:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found or server restarted",
        )

    return RedirectResponse(url=long_url, status_code=302)


import os

PUBLIC_BASE_URL = os.getenv(
    "PUBLIC_BASE_URL", "http://127.0.0.1:8000"
).rstrip("/")



# if __name__ == "__main__":

#     shortner = URLShortner()

#     url1 = "https://www.youtube.com/watch?v=MZ5Si3kkWTI&list=PLM6furP1T9ouXchvDSr_jkiMOt9qTnevp&index=4"
#     url2 = "https://github.com/padariya-tech/Ecommerce-APP"

#     s1 = shortner.shorten(url1)
#     s2 = shortner.shorten(url2)

#     print("Short URL for url1: ", s1)
#     print("Short URL for url2: ",s2)
    
