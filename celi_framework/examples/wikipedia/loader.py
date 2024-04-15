from bs4 import BeautifulSoup, NavigableString
from dataclasses import dataclass, field
from typing import List, Optional, Dict

from celi_framework.examples.wikipedia.wikipedia_utils import get_cached_session


__all__ = [
    "ContentHierarchyNode",
    "ContentReference",
    "load_content_from_wikipedia_url",
]


@dataclass
class ContentReference:
    """A numbered reference with an external link from a wikipedia article.

    References that don't have a URL, or that just reference another citation are not included in this list, so all numbered references in the article may not be found.

    Attributes:
        number: The reference number used within the article.  Starts at 1 and goes to the nubmer of references.
        title: The text associated with the reference link in the "References" section of the wikipedia article.
        href: The page anchor for this reference.  This uniquely identifies the reference on the page.
        url: The url asswociated with the reference.  This is the link to the referenced content.
    """

    number: str
    title: str
    href: str
    url: str


@dataclass
class ContentHierarchyNode:
    """A section of a wikipedia article associated with an entry in the table of contents.

    Includes the content associated with this entry, any references, as well as child objects containing any subsections.
    """

    number: str
    title: str
    href: str
    content: Optional[str] = None
    children: List["ContentHierarchyNode"] = field(default_factory=list)
    references: List[ContentReference] = field(default_factory=list)

    def add_child(self, child: "ContentHierarchyNode"):
        self.children.append(child)

    def add_reference(self, reference: ContentReference):
        self.references.append(reference)

    def add_references(self, references: List[ContentReference]):
        self.references.extend(references)

    def add_content(self, content: str):
        assert self.content is None
        self.content = content


def load_content_from_wikipedia_url(url: str, include_references: bool = True):
    """Loads a wikipedia article from a URL, sections based on the table of contents and extracts referneces."""

    # Cache http requests for easier offline operation.
    session = get_cached_session()

    html_content = session.get(url=url).text
    soup = BeautifulSoup(html_content, "html.parser")
    toc = extract_toc(soup)
    references = extract_references(soup) if include_references else []
    attach_content_and_reference(soup, toc, references)
    return toc, references


def extract_toc(soup: BeautifulSoup) -> List[ContentHierarchyNode]:
    def create_toc_entry(element) -> ContentHierarchyNode:
        for child in element.children:
            if child.name == "a":
                text = child.get_text(separator=" ", strip=True)
                number, title = text.split(" ", 1) if " " in text else ("", text)
                href = child["href"].replace("#", "")
                node = ContentHierarchyNode(number.strip(), title.strip(), href=href)
                return node
        raise ValueError("No link found in TOC entry")

    def process_list_items(ul_element) -> List[ContentHierarchyNode]:
        items = []
        for li in ul_element.find_all("li", recursive=False):
            node = create_toc_entry(li)
            nested_ul = li.find("ul")
            if nested_ul:
                for child in process_list_items(nested_ul):
                    node.add_child(child)
            items.append(node)
        return items

    toc_list = soup.find(
        "ul", {"class": "vector-toc-contents", "id": "mw-panel-toc-list"}
    )
    if not toc_list:
        raise ValueError("Table of contents not found")

    return process_list_items(toc_list)


def extract_references(soup: BeautifulSoup) -> List[ContentReference]:
    reference_lists = soup.find_all("ol", {"class": "references"})
    references = []
    for reference_list in reference_lists:
        for (
            ix,
            li,
        ) in enumerate(reference_list.find_all("li", recursive=False)):
            href = li["id"]
            number = str(ix + 1)
            link = li.find("a", {"class": "external text"})
            if link:
                title = link.get_text(separator=" ", strip=True)
                url = link["href"]
                ref = ContentReference(number, title, href, url)
                references.append(ref)
    return references


def flatten_toc(toc: List[ContentHierarchyNode]) -> List[ContentHierarchyNode]:
    def flatten(node: ContentHierarchyNode) -> List[ContentHierarchyNode]:
        nodes = [node]
        for child in node.children:
            nodes.extend(flatten(child))
        return nodes

    return [node for root in toc for node in flatten(root)]


def format_content(toc: List[ContentHierarchyNode]) -> str:
    flat_nodes = flatten_toc(toc)
    return "\n".join(
        f"{node.number} {node.title}\n{node.content}\n\n" for node in flat_nodes
    )


def recurse_ids_and_text(
    soup: BeautifulSoup, reference_dict: Dict[str, ContentReference]
):
    """Returns a tuple of id, text, reference pairs for all elements."""

    def recurse(element):
        if isinstance(element, NavigableString):
            return [(None, element, None)]
        if element.name in ["script", "style"]:
            return []
        reference = (
            reference_dict[element.a["href"].replace("#", "")]
            if element.name == "sup"
            and "reference" in element.get("class", [])
            and element.a
            and element.a.get("href", "").replace("#", "") in reference_dict
            else None
        )
        if element.children:
            children = [_ for child in element.children for _ in recurse(child)]
        else:
            children = []
        return [(element.get("id", None), None, reference)] + children

    content_div = soup.find("div", id="bodyContent")
    return recurse(content_div)


def attach_content_and_reference(
    soup: BeautifulSoup,
    toc: List[ContentHierarchyNode],
    references: List[ContentReference],
):
    reference_dict = {_.href: _ for _ in references}
    flattened_text = recurse_ids_and_text(soup, reference_dict)
    flat_toc = flatten_toc(toc)
    current_ix = 0
    next_id = flat_toc[current_ix + 1].href
    current_text = ""
    current_references = []
    for id, text, reference in flattened_text:
        if id == next_id:
            flat_toc[current_ix].add_content(current_text)
            flat_toc[current_ix].add_references(current_references)
            current_text = ""
            current_references = []
            current_ix += 1
            if current_ix < len(flat_toc) - 1:
                next_id = flat_toc[current_ix + 1].href
            else:
                next_id = -1  # Something unmatchable
        if text:
            current_text += " " + text
        if reference:
            current_references.append(reference)
    flat_toc[current_ix].add_content(current_text)
    flat_toc[current_ix].add_references(current_references)
