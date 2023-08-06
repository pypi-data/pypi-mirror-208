from collections.abc import AsyncIterator
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import unquote
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from bs4 import ResultSet
from bs4 import Tag
from httpx import AsyncClient
from httpx import Response

from visual_novel_toolkit.speller.mistakes import load_mistakes
from visual_novel_toolkit.speller.words import FileWords


async def proofread_mistakes() -> None:
    mistakes = {word for word, _source, _suggestions in load_mistakes()}
    if not mistakes:
        return

    file_words = FileWords(Path("wiktionary.json"))
    dictionary = file_words.loads()

    words: set[str] = set()

    await scrap_wiktionary(mistakes, words)

    if not words:
        return

    dictionary.extend(words)
    dictionary.sort()
    file_words.dumps(dictionary)


async def scrap_wiktionary(mistakes: set[str], words: set[str]) -> None:
    async with AsyncClient() as client:
        for mistake in mistakes:
            async for address, page in search(client, mistake):
                correct = [address]
                correct.extend(scrap_all_tables(page))
                if mistake in correct or mistake.lower() in correct:
                    words.add(mistake)
                    break


async def search(client: AsyncClient, mistake: str) -> AsyncIterator[tuple[str, bytes]]:
    response = await form_search(client, mistake)
    if response.url.path.startswith("/wiki/"):
        yield response.url.path.removeprefix("/wiki/"), response.content
    else:
        for url in scrap_all_forms(response.content):
            response1 = await page_table(client, url)
            yield response1.url.path.removeprefix("/wiki/"), response1.content


async def form_search(client: AsyncClient, mistake: str) -> Response:
    return await client.get(
        "https://ru.wiktionary.org/w/index.php",
        params={"search": mistake},
        follow_redirects=True,
    )


async def page_table(client: AsyncClient, url: str) -> Response:
    return await client.get(url, follow_redirects=True)


def scrap_all_forms(content: bytes) -> Iterator[str]:
    soup = BeautifulSoup(content, "html.parser")
    containers: ResultSet[Tag] = soup.select("div.mw-search-results-container")
    for container in containers:
        yield from scrap_single_form(container)


def scrap_single_form(container: Tag) -> Iterator[str]:
    links: ResultSet[Tag] = container.select("a")
    for a in links:  # pragma: no branch
        href = a.get("href")
        if isinstance(href, str):  # pragma: no branch
            url = urlparse(unquote(href))
            if url.path.startswith("/wiki/"):  # pragma: no branch
                yield f"https://ru.wiktionary.org{href}"


def scrap_all_tables(content: bytes) -> Iterator[str]:
    soup = BeautifulSoup(content, "html.parser")
    tables: ResultSet[Tag] = soup.select("table.morfotable")
    for table in tables:
        yield from scrap_single_table(table)


def scrap_single_table(table: Tag) -> Iterator[str]:
    cells: ResultSet[Tag] = table.select("td")
    for cell in cells:
        for text in cell.stripped_strings:
            for part in text.split():
                yield part.replace("̀", "").replace("́", "")
