import httpx
from bs4 import BeautifulSoup

from urllib.parse import urljoin, urlparse


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

def get_same_domain_links(
    base_url: str,
    soup: BeautifulSoup
):
    base_domain = urlparse(base_url).netloc

    links = []

    for link in soup.find_all("a", href=True):
        absolute_url = urljoin(base_url, link["href"])

        if urlparse(absolute_url).netloc == base_domain:
            links.append(absolute_url)

    return links

import asyncio

async def crawl(
    start_url: str,
    max_pages: int = 3,
    progress_callback=None
):
    visited = set()
    pages = []

    async with httpx.AsyncClient(
        timeout=10.0,
        headers={
            "User-Agent": "FastAPI-Practice-Scraper/1.0"
        }
    ) as client:

        urls_to_visit = [start_url]

        while urls_to_visit and len(pages) < max_pages:

            url = urls_to_visit.pop(0)

            if url in visited:
                continue

            visited.add(url)

            try:
                response = await client.get(url)
                response.raise_for_status()

            except httpx.HTTPError as exc:
                print(f"Failed to fetch {url}: {exc}")
                continue

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            title = soup.title.get_text(strip=True)

            text = soup.get_text(
                " ",
                strip=True
            )

            pages.append({
                "url": url,
                "title": title,
                "text": text[:500]
            })
            if progress_callback:
                progress = int(
                    len(pages) / max_pages * 100
                )

                await progress_callback(progress)
            await asyncio.sleep(1)  # Be polite and avoid overwhelming the server
            print(f"Scraped page {len(pages)}: {url}")

            links = get_same_domain_links(
                url,
                soup
            )

            for link in links:
                if link not in visited and link not in urls_to_visit:
                    urls_to_visit.append(link)

    return pages





