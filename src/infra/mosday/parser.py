import re
from datetime import datetime
from itertools import islice

from bs4 import BeautifulSoup, SoupStrainer, Tag

from src.domain.news.models import NewsEntry
from src.utils.dt import make_aware, now

from .dto import NewsEntryFromRss


class MosDayParser:
    _id_expr = re.compile(r"\?(\d*)")
    _dt_string_expr = re.compile(r"\d{2}.\d{2}.\d{4} \d{2}:\d{2}")
    _date_string_expr = re.compile(r"\d{2}.\d{2}.\d{4}")
    _fallback_preview_url = "https://mosday.ru/404"

    def extract_latest_news_id(self, xml: bytes):
        strainer = SoupStrainer("item")
        soup = BeautifulSoup(xml, "xml", parse_only=strainer)
        item = soup.find("item")
        if not item:
            return
        link = item.find("link")
        if not isinstance(link, Tag):
            return
        return self._extract_id_from_path(link.get_text())

    def parse_news_from_rss(self, xml: bytes, latest_news_id: str | None):
        strainer = SoupStrainer("item")
        soup = BeautifulSoup(xml, "xml", parse_only=strainer)
        items: list[Tag] = soup.find_all("item")
        parsed_date = now()
        pub_date_fmt = "%a, %d %b %Y %H:%M:%S %z"
        for item in items:
            link = item.find("link")
            if not isinstance(link, Tag):
                continue
            id_ = self._extract_id_from_path(link.get_text())
            if id_ == latest_news_id:
                return
            title_tag = item.find("title")
            if not isinstance(title_tag, Tag):
                continue
            title = title_tag.get_text()
            enclosure_tag = item.find("enclosure")
            if isinstance(enclosure_tag, Tag):
                preview_url = enclosure_tag["url"]
            else:
                preview_url = self._fallback_preview_url
            pub_date_tag = item.find("pubDate")
            if not isinstance(pub_date_tag, Tag):
                continue
            pub_date = datetime.strptime(pub_date_tag.get_text(), pub_date_fmt)
            yield NewsEntryFromRss(
                id=id_,
                title=title,
                preview_url=preview_url,
                pub_date=pub_date,
                parsed_date=parsed_date,
            )

    def extract_tags_from_detail(self, html: bytes):
        soup = BeautifulSoup(html, "lxml")
        article = soup.find("article")
        if not isinstance(article, Tag):
            return
        font = article.find("font", {"color": "#666666"})
        if not isinstance(font, Tag):
            return
        return [self._extract_tag_from_href(link["href"]) for link in font.find_all("a")]

    def parse_news(
        self,
        html: bytes,
        tag: str,
        latest_news_id: str | None = None,
    ):
        tr: Tag
        image_block: Tag
        content_block: Tag
        if latest_news_id:

            def condition(id_: str):
                return id_ == latest_news_id

        else:

            def condition(id_: str):
                return False

        parsed_date = now()
        pub_date_fmt = "%d.%m.%Y %H:%M"
        strainer = SoupStrainer("table", {"width": "95%"})
        soup = BeautifulSoup(html, "lxml", parse_only=strainer)
        news: list[NewsEntry] = []
        for tr in soup.find_all("tr"):
            blocks = tr.find_all("td")
            if len(blocks) != 2:
                continue
            image_block, content_block = blocks
            a_tag = content_block.find("a")
            if not isinstance(a_tag, Tag):
                continue
            href = a_tag["href"]
            if not isinstance(href, str):
                continue
            id_ = self._extract_id_from_path(href)
            if not id_:
                continue
            if condition(id_):
                break
            image = image_block.find("img")
            if isinstance(image, Tag):
                preview_url = self._build_preview_url(image['src'])
            else:
                preview_url = self._fallback_preview_url
            pub_date_string = "".join(islice(content_block.strings, 2))[:16]
            if not self._is_valid_dt_string(pub_date_string):
                if not self._is_valid_date_string(pub_date_string[:10]):
                    continue
                pub_date_string=f"{pub_date_string[:10]} 00:00"
            pub_date = make_aware(datetime.strptime(pub_date_string, pub_date_fmt))
            title = a_tag.get_text(strip=True)
            news.append(
                NewsEntry(
                    id=id_,
                    tag=tag,
                    title=title,
                    preview_url=preview_url,
                    pub_date=pub_date,
                    parsed_date=parsed_date,
                )
            )
        return news

    def _build_preview_url(self, path: str):
        return f"https://mosday.ru/news/{path}"

    def _tag_condition(self, tag: Tag):
        href = tag.get("href")
        if isinstance(href, str) and href.startswith("tags.php?") and "=" not in href:
            return True

    def _extract_tag_from_href(self, href: str) -> str:
        return href.rsplit("?", 1)[-1]

    def _extract_id_from_path(self, path: str) -> str:
        match = self._id_expr.search(path)
        if match:
            return match.group(1)
        raise RuntimeError(f"not found news id in path '{path}'")

    def _is_valid_dt_string(self, dt_string: str):
        return self._dt_string_expr.fullmatch(dt_string)
    def _is_valid_date_string(self, dt_string: str):
        return self._date_string_expr.fullmatch(dt_string)
