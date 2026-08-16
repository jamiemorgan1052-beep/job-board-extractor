from __future__ import annotations

from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from typing import Iterable
from urllib.parse import urljoin


@dataclass(frozen=True)
class SelectorConfig:
    card: str
    title: str
    company: str
    location: str
    link: str
    description: str | None = None


@dataclass(frozen=True)
class Job:
    title: str
    company: str
    location: str
    url: str
    description: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ExtractionResult:
    jobs: tuple[Job, ...]
    warnings: tuple[str, ...]


@dataclass
class _Node:
    tag: str
    attrs: dict[str, str]
    children: list["_Node"]
    text_chunks: list[str]

    @property
    def text(self) -> str:
        parts = list(self.text_chunks)
        parts.extend(child.text for child in self.children)
        return " ".join(" ".join(parts).split())


class _TreeParser(HTMLParser):
    _void_tags = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("document", {}, [], [])
        self._stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = _Node(tag.lower(), {key.lower(): value or "" for key, value in attrs}, [], [])
        self._stack[-1].children.append(node)
        if tag.lower() not in self._void_tags:
            self._stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in self._void_tags:
            self._stack.pop()

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        for index in range(len(self._stack) - 1, 0, -1):
            if self._stack[index].tag == lowered:
                del self._stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if data.strip():
            self._stack[-1].text_chunks.append(data)


def _matches(node: _Node, selector: str) -> bool:
    selector = selector.strip()
    if not selector or any(character in selector for character in " >+~[:"):
        raise ValueError(f"Unsupported selector: {selector!r}")
    tag = ""
    identifier = ""
    classes: list[str] = []
    token = ""
    mode = "tag"
    for character in selector:
        if character in ".#":
            if mode == "tag":
                tag = token
            elif mode == "class":
                classes.append(token)
            else:
                identifier = token
            token = ""
            mode = "class" if character == "." else "id"
        else:
            token += character
    if mode == "tag":
        tag = token
    elif mode == "class":
        classes.append(token)
    else:
        identifier = token
    node_classes = set(node.attrs.get("class", "").split())
    return (
        (not tag or node.tag == tag.lower())
        and (not identifier or node.attrs.get("id") == identifier)
        and all(class_name in node_classes for class_name in classes if class_name)
    )


def _walk(node: _Node) -> Iterable[_Node]:
    for child in node.children:
        yield child
        yield from _walk(child)


def _find(node: _Node, selector: str) -> _Node | None:
    return next((candidate for candidate in _walk(node) if _matches(candidate, selector)), None)


def extract_jobs(html: str, base_url: str, config: SelectorConfig) -> ExtractionResult:
    parser = _TreeParser()
    parser.feed(html)
    cards = [node for node in _walk(parser.root) if _matches(node, config.card)]
    jobs: list[Job] = []
    warnings: list[str] = []
    seen: set[tuple[str, str, str]] = set()

    for index, card in enumerate(cards, start=1):
        title_node = _find(card, config.title)
        company_node = _find(card, config.company)
        location_node = _find(card, config.location)
        link_node = _find(card, config.link)
        missing = [
            name
            for name, node in (("title", title_node), ("company", company_node), ("location", location_node), ("link", link_node))
            if node is None or (name != "link" and not node.text)
        ]
        href = link_node.attrs.get("href", "").strip() if link_node else ""
        if not href:
            missing.append("link href")
        if missing:
            warnings.append(f"card {index}: skipped; missing {', '.join(missing)}")
            continue

        description_node = _find(card, config.description) if config.description else None
        job = Job(
            title=title_node.text,
            company=company_node.text,
            location=location_node.text,
            url=urljoin(base_url, href),
            description=description_node.text if description_node else "",
        )
        key = (job.title.casefold(), job.company.casefold(), job.url)
        if key in seen:
            warnings.append(f"card {index}: duplicate skipped")
            continue
        seen.add(key)
        jobs.append(job)

    return ExtractionResult(tuple(jobs), tuple(warnings))
