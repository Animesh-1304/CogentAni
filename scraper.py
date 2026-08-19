import httpx
from bs4 import BeautifulSoup


async def scrape_page(url: str):
    async with httpx.AsyncClient(
        timeout=10.0,
        headers={
            "User-Agent": "FastAPI-Practice-Scraper/1.0"
        }
    ) as client:

        response = await client.get(url)

        print("Status:", response.status_code)

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.get_text(strip=True)

        text = soup.get_text(" ", strip=True)

        return {
            "url": url,
            "title": title,
            "text": text[:500]
        }


import asyncio


async def main():
    result = await scrape_page(
        "https://books.toscrape.com/"
    )

    print("\nTitle:")
    print(result["title"])

    print("\nText snippet:")
    print(result["text"])


if __name__ == "__main__":
    asyncio.run(main())