"""
Solshal service to scrap websites
"""
import os
import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup as soup

app = Flask(__name__)

MESSAGES = {
    "INVALID_URL": "Not able to automatically parse the url.",
    "SOMETHING_WRONG": "Sorry but something went wrong and the request wasn't able to complete."
}

@app.route("/scrap", methods=["POST"])
def scrap_url():
    """
    Receive an url and pass to Scrapy to scam
    Returns url, title, description, thumbnail
    """
    data = request.get_json()
    url = data["url"]
    pageContent = request_url(url)

    if pageContent == None:
        return jsonify({
            "message": MESSAGES["SOMETHING_WRONG"],
            "data": {}
        }), 400

    if isinstance(pageContent, dict):
        invalidContent = get_invalid_content(url=url, contentType=pageContent["Content-Type"])

        return jsonify({
            "message": MESSAGES["INVALID_URL"],
            "data": invalidContent
        }), pageContent["code"]

    parsedHTML = soup(pageContent, "html.parser")
    validContent = get_valid_content(parsedHTML, url)

    return jsonify({
        "data": validContent
    }), 200

def request_url(url):
    """Get url content and check if it returns 200
    if so check if Content-Type is HTML otherwise throw
    
    Arguments:
        url {String} -- url domain
    
    Returns:
        [String] -- if 200 and Content-Type HTML successful returns content
        [Int] -- if 200 but Content-Type NOT HTML returns status code 206
        [None] -- if NOT 200 or exception returns None
    """

    try:
        response = requests.get(url, timeout=3)
        
        if response.status_code == 200:
            contentType = response.headers["Content-Type"]
            isValidDocType = is_valid_doc_type(contentType)
            
            if isValidDocType is not True:
                return {
                    "code": 206,
                    "Content-Type": contentType
                }

            return response.content

    except (
        requests.exceptions.InvalidURL,
        requests.exceptions.ContentDecodingError,
        requests.exceptions.Timeout, 
        requests.exceptions.TooManyRedirects,
        requests.exceptions.RequestException):
        return None

def is_valid_doc_type(contentType):
    """Check if page content is other than HTML doctype
    
    Arguments:
        contentType {String} -- page Content-Type (pdf/json/html/mp3/etc)
    
    Returns:
        [Boolen] -- Returns True if doctype is html otherwise False
    """
    if "text/html" not in contentType:
        return False

    return True

def get_invalid_content(url, contentType):
    """Returns expected collection format but only with url
    
    Arguments:
        url {String} -- url domain
        contentType {String} -- request content-type
    
    Returns:
        [Dict] -- collection format
    """
    ACCEPTED_THUMBNAIL = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ]
    thumbnail = ""

    if any(type in contentType for type in ACCEPTED_THUMBNAIL):
        thumbnail = url
    

    collection = {
        "title": "Untitled - EDIT ME",
        "description": "",
        "url": url,
        "thumbnail": thumbnail
    }

    return collection

def get_valid_content(content, url):
    """
    Get content from metas and return object formated
    """
    title = content.title.string if content.title != "" else "Untitled"
    description = get_meta_content(
        content.select("meta[property='og:description']"),
        content.select("meta[name=description]")
    )
    thumbnail = get_meta_content(content.select("meta[property='og:image']"), valueB=None)

    collection = {
        "title": title,
        "description": description,
        "url": url,
        "thumbnail": thumbnail
    }

    return collection

def get_meta_content(valueA, valueB):
    """
    Check if value a is empty if so
    checks value b
    """
    valueA = valueA[0]["content"] if valueA else ""
    valueB = valueB[0]["content"] if valueB else ""

    if valueA == "":
        return valueB

    return valueA

if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = os.getenv("PORT", 5000)

    app.run(
        host=HOST,
        port=PORT
    )
