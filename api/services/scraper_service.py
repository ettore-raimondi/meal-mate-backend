from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

import requests

from venv import logger
from api.models.menu_item import MenuItem
from api.services.gemini_service import GeminiService
from bs4 import BeautifulSoup, Tag



class ScraperService:
    MENU_KEYWORDS = (
        "menu",
        "order",
        "food",
        "drink",
        "dishes",
        "specials",
        "lunch",
        "dinner",
        "breakfast",
        "appetizer",
        "speisekarte",
        "karte",
        "mittag",
        "abend",
        "getränke",
        "gerichte",
        "essen",
    )
    MAX_TEXT_CHARS = 2000
    MAX_MENU_SECTIONS = 16
    FALLBACK_SECTION_LIMIT = 6
    KEYWORD_CONTEXT_DEPTH = 3
    CHUNK_WORKERS = 3

    def __init__(self):
        self.gemini = GeminiService()

    def truncate_text(self, text: str, limit: int | None = None) -> str:
        if limit is None:
            limit = self.MAX_TEXT_CHARS
        if limit <= 0 or len(text) <= limit:
            return text
        return text[:limit]

    def chunk_text(self, text: str, chunk_size: int | None = None) -> list[str]:
        if not text:
            return []
        if chunk_size is None:
            chunk_size = self.MAX_TEXT_CHARS
        chunks: list[str] = []
        for start in range(0, len(text), chunk_size):
            end = min(len(text), start + chunk_size)
            chunks.append(text[start:end])
        return chunks

    def _collect_relevant_sections(self, soup: BeautifulSoup) -> list[str]:
        sections: list[str] = []
        for tag in soup.find_all(["section", "div", "article", "ul", "ol", "nav"]):
            snippet = tag.get_text(" ", strip=True)
            lowered = snippet.lower()
            if any(keyword in lowered for keyword in self.MENU_KEYWORDS):
                sections.append(snippet)
            if len(sections) >= 8:
                break
        return sections

    def _gather_keyword_focus_tags(self, soup: BeautifulSoup) -> list[Tag]:
        focus_tags: list[Tag] = []
        seen: set[int] = set()

        for text_node in soup.find_all(string=True):
            if not text_node:
                continue
            lowered = text_node.strip().lower()
            if not lowered:
                continue
            if any(keyword in lowered for keyword in self.MENU_KEYWORDS):
                parent = text_node.parent
                depth = 0
                while parent and depth < self.KEYWORD_CONTEXT_DEPTH:
                    if isinstance(parent, Tag):
                        identifier = id(parent)
                        if identifier not in seen:
                            focus_tags.append(parent)
                            seen.add(identifier)
                    parent = parent.parent
                    depth += 1
        return focus_tags

    def _looks_like_menu_container(self, tag: Tag) -> bool:
        identifier_bits: list[str] = []
        tag_id = tag.get("id")
        if tag_id:
            identifier_bits.append(str(tag_id))
        tag_classes = tag.get("class") or []
        identifier_bits.extend(tag_classes)
        identifier = " ".join(identifier_bits).lower()
        if any(keyword in identifier for keyword in self.MENU_KEYWORDS):
            return True
        snippet = tag.get_text(" ", strip=True).lower()
        snippet = snippet[:500]
        return any(keyword in snippet for keyword in self.MENU_KEYWORDS)

    def _annotate_links_and_media(self, node: BeautifulSoup | Tag, base_url: str | None) -> None:
        if not base_url:
            return
        for anchor in node.find_all("a"):
            href = urljoin(base_url, anchor.get("href", ""))
            label = anchor.get_text(strip=True) or href
            anchor.replace_with(f"{label} [link: {href}]")
        for image in node.find_all("img"):
            src = image.get("src")
            if not src:
                continue
            resolved_src = urljoin(base_url, src)
            alt_text = image.get("alt", "").strip() or "Menu image"
            image.replace_with(f"{alt_text} [image: {resolved_src}]")

    def _build_relevant_text_blocks(
        self,
        soup: BeautifulSoup,
        base_url: str | None,
        *,
        include_links: bool,
    ) -> list[str]:
        candidate_tags: list[Tag] = []
        seen_ids: set[int] = set()
        for idx, tag in enumerate(soup.find_all(["section", "div", "article", "ul", "ol", "table"])):
            if self._looks_like_menu_container(tag):
                identifier = id(tag)
                if identifier not in seen_ids:
                    candidate_tags.append(tag)
                    seen_ids.add(identifier)
            elif idx < self.FALLBACK_SECTION_LIMIT:
                identifier = id(tag)
                if identifier not in seen_ids:
                    candidate_tags.append(tag)
                    seen_ids.add(identifier)
            if len(candidate_tags) >= self.MAX_MENU_SECTIONS:
                break

        for focus_tag in self._gather_keyword_focus_tags(soup):
            identifier = id(focus_tag)
            if identifier in seen_ids:
                continue
            candidate_tags.append(focus_tag)
            seen_ids.add(identifier)
            if len(candidate_tags) >= self.MAX_MENU_SECTIONS:
                break

        if not candidate_tags:
            body = soup.body
            if body:
                candidate_tags = [body]
            else:
                candidate_tags = [soup]

        text_blocks: list[str] = []
        for candidate in candidate_tags:
            fragment = BeautifulSoup(str(candidate), "html.parser")
            for tag in fragment(["script", "style", "noscript"]):
                tag.decompose()
            if include_links:
                self._annotate_links_and_media(fragment, base_url)
            block_text = fragment.get_text("\n", strip=True)
            if block_text:
                text_blocks.append(block_text)

        return text_blocks

    def fetch_html(self, url: str) -> str:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "MealMateBot/1.0"})
        resp.raise_for_status()
        return resp.text
    
    def extract_text_with_links(self, html: str, base_url: str, *, limit: int | None = None) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text_blocks = self._build_relevant_text_blocks(soup, base_url, include_links=True)
        text = "\n\n".join(text_blocks)
        return self.truncate_text(text, limit)
    
    def extract_text(self, html: str, *, limit: int | None = None) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text_blocks = self._build_relevant_text_blocks(soup, base_url=None, include_links=False)
        text = "\n\n".join(text_blocks)
        return self.truncate_text(text, limit)
    
    def scrape_menu_from_image(self, image_url: str) -> list[MenuItem]:
        # TODO: Implement menu scraping from image using Gemini or another OCR service
        logger.info(f"Scraping menu from image: {image_url}")

        # For now, we'll just return an empty list since this is a more complex feature to implement and may require additional services or APIs.
        return []
        
    def invoke_gemini_menu_parser(self, stripped_menu_text: str) -> list[MenuItem]:
        response = self.gemini.client.models.generate_content(
            model=self.gemini.model_name,
            contents=[{
                "role": "user",
                "parts": [
                    {"text": "Your job, is to scrape the menu items from a website. I will give you the html of the website, and you will return a list of menu items. Each menu item should have a name, description, price, and image url. I need this information as JSON, and I need it to be as accurate as possible. If you are not sure about the price, return null for the price. If you are not sure about the description, return an empty string for the description. If you are not sure about the image url, return an empty string for the image url."},
                    {"text": stripped_menu_text},
                ],
            }],
            config={
                "response_mime_type": "application/json",
                "response_json_schema": {
                    "type": "object",
                    "properties": {
                        "menu_items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "price": {"type": "number"},
                                    "image_url": {"type": "string"},
                                }
                            }
                        }
                    }
                },
            },
        )

        menu_items_data = response.model_dump().get('parsed', {}).get("menu_items", []) or []
        return [
            MenuItem(
                name=item.get("name", ""),
                description=item.get("description", ""),
                price=item.get("price"),
                image_url=item.get("image_url", ""),
            )
            for item in menu_items_data
        ]

    def _parse_menu_chunks(self, text_chunks: list[str]) -> list[MenuItem]:
        if not text_chunks:
            return []
        if len(text_chunks) == 1:
            return self.invoke_gemini_menu_parser(text_chunks[0])

        max_workers = max(1, min(self.CHUNK_WORKERS, len(text_chunks)))
        ordered_results: dict[int, list[MenuItem]] = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.invoke_gemini_menu_parser, chunk): index
                for index, chunk in enumerate(text_chunks)
            }
            for future in as_completed(futures):
                index = futures[future]
                ordered_results[index] = future.result()

        aggregated: list[MenuItem] = []
        for index in range(len(text_chunks)):
            aggregated.extend(ordered_results.get(index, []))
        return aggregated

    def scrape_menu_from_url(self, website_url: str, menu_url: str) -> list[MenuItem]:
        logger.info(f"Scraping menu from URL: {menu_url}")
        url = urljoin(website_url, menu_url.strip())
        menu_html = self.fetch_html(url)
        stripped_menu_text = self.extract_text_with_links(menu_html, url, limit=0)
        text_chunks = self.chunk_text(stripped_menu_text)
        if not text_chunks:
            text_chunks = [stripped_menu_text]

        try:
            return self._parse_menu_chunks(text_chunks)
        except Exception as exc:
            logger.exception("Menu scraping failed")
            raise RuntimeError("Unable to scrape menu from URL") from exc

    def menu_scraper(self, website_url: str) -> list[MenuItem]:
        # Need to fetch all the html from the website and then pass it to GEMINI bro, so it can scrape da info
        html = self.fetch_html(website_url)
        stripped_text = self.extract_text_with_links(html, website_url)

        # Tell AI to find the menu link  on the website.
        # TODO: we can improve this prompt by asking the AI to look for specific keywords in the anchor text, like "menu", "order", "food", "drink", "dishes", "specials", "lunch", "dinner", "breakfast", "appetizer", etc. We can also ask the AI to look for images that might be menus, and if it finds any, to return the image url as well.
        menu_response = self.gemini.client.models.generate_content(
            model=self.gemini.model_name,
            contents=f"Your job is to find the menu page for a restaurant's website. I will give you the html of the homepage of the restaurant's website, and you will return the url of the menu page. If you can't find a menu page, return null. If you find an image that looks like it could be a menu, return the image url as well. Here is the html: {stripped_text}",
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": {
                        "type": "object",
                        "properties": {
                            "menu_url": {"type": ["string", "null"]},
                            "image_url": {"type": ["string", "null"]},
                            "reason": {"type": ["string", "null"]},
                        }
                    }
                },
            )
        menu_response_json = menu_response.model_dump().get('parsed')

        menu_url = menu_response_json.get("menu_url")
        image_url = menu_response_json.get("image_url")

        scraped_menu_items: list[MenuItem]
        if menu_url:
            scraped_menu_items = self.scrape_menu_from_url(website_url, menu_url)
        elif image_url:
            scraped_menu_items = self.scrape_menu_from_image(image_url)
        else:
            logger.warning(f"Menu scraping failed to find a menu URL or image for {website_url}. Reason: {menu_response_json.get('reason')}")
            scraped_menu_items = []
        
        return scraped_menu_items