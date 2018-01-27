"""
Solshal service to scrap websites
"""
import os
import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup as soup

app = Flask(__name__)

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
            "message": "Not able to parse the url"
        }), 400

    parsedHTML = soup(pageContent, "html.parser")
    formattedContent = format_content(parsedHTML, url)

    return jsonify({
        "data": formattedContent
    }), 200

def request_url(url):
    """
    Request url and return the markup
    """
    try:
        page = requests.get(url, timeout=5)
        if page.status_code == 200:
            return page.content
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.TooManyRedirects:
        return None
    except requests.exceptions.RequestException as error:
        return None

def format_content(content, url):
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
    app.run(
        port=os.getenv("PORT", 5500)
    )
