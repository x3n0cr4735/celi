from bs4 import BeautifulSoup, NavigableString
from dataclasses import dataclass, field
from typing import List, Optional, Dict

from celi_framework.examples.wikipedia.wikipedia_utils import get_cached_session


__all__ = [
    "ContentHierarchyNode",
    "ContentReference",
    "load_content_from_wikipedia_url",
    "format_content",
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
    """
    Extracts the table of contents (TOC) from a BeautifulSoup object representing a Wikipedia article.
    
    Args:
        soup (BeautifulSoup): A BeautifulSoup object representing a Wikipedia article.
        
    Returns:
        List[ContentHierarchyNode]: A list of ContentHierarchyNode objects representing the TOC entries.
        
    Raises:
        ValueError: If the table of contents is not found in the BeautifulSoup object.
        
    This function recursively extracts the table of contents from a Wikipedia article represented by a BeautifulSoup object. It does this by finding the unordered list element with the class "vector-toc-contents" and the id "mw-panel-toc-list". It then processes each list item in the unordered list, creating a ContentHierarchyNode object for each list item. If a list item has nested unordered lists, the function recursively processes those nested lists as well. The function returns a list of ContentHierarchyNode objects representing the TOC entries.
    """
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
        """
        Recursively processes a list of items in an unordered list element and creates a list of ContentHierarchyNode objects representing the TOC entries.

        Args:
            ul_element (BeautifulSoup): The unordered list element to process.

        Returns:
            List[ContentHierarchyNode]: A list of ContentHierarchyNode objects representing the TOC entries.

        This function iterates over each list item in the given unordered list element and creates a ContentHierarchyNode object for each list item. If a list item has nested unordered lists, the function recursively processes those nested lists as well. The function returns a list of ContentHierarchyNode objects representing the TOC entries.
        """
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
    """
    Extracts references from a BeautifulSoup object and returns a list of ContentReference objects.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object representing the HTML document.

    Returns:
        List[ContentReference]: A list of ContentReference objects representing the extracted references.

    The function searches for all <ol> elements with the class "references" in the given BeautifulSoup object.
    For each <ol> element, it iterates over its <li> elements and extracts the reference information.
    The reference information includes the reference number, title, href, and url.
    The function creates a ContentReference object for each extracted reference and appends it to the references list.
    Finally, it returns the references list.

    Note:
        - The function assumes that the BeautifulSoup object represents a valid HTML document.
        - The function assumes that the <ol> elements with the class "references" contain valid <li> elements.
        - The function assumes that each <li> element has an "id" attribute.
        - The function assumes that each <li> element contains an <a> element with the class "external text".
        - The function assumes that the <a> element has a "href" attribute.

    Example:
        >>> html = "<ol class='references'><li id='ref1'><a class='external text' href='https://example.com'>Reference 1</a></li><li id='ref2'><a class='external text' href='https://example.com'>Reference 2</a></li></ol>"
        >>> soup = BeautifulSoup(html, 'html.parser')
        >>> extract_references(soup)
        [ContentReference(number='1', title='Reference 1', href='ref1', url='https://example.com'), ContentReference(number='2', title='Reference 2', href='ref2', url='https://example.com')]
    """
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
    """
    Flattens a table of contents (TOC) by recursively traversing the hierarchy of nodes.

    Args:
        toc (List[ContentHierarchyNode]): The table of contents to flatten.

    Returns:
        List[ContentHierarchyNode]: The flattened table of contents.
    """
    def flatten(node: ContentHierarchyNode) -> List[ContentHierarchyNode]:
        nodes = [node]
        for child in node.children:
            nodes.extend(flatten(child))
        return nodes

    return [node for root in toc for node in flatten(root)]


def format_content(toc: List[ContentHierarchyNode]) -> str:
    """
    Formats the content of a table of contents (TOC) into a string.

    Args:
        toc (List[ContentHierarchyNode]): The table of contents to format.

    Returns:
        str: The formatted content of the table of contents. Each node is represented by its number, title, and content,
        separated by newlines.
    """
    flat_nodes = flatten_toc(toc)
    return "\n".join(
        f"{node.number} {node.title}\n{node.content}\n\n" for node in flat_nodes
    )


def recurse_ids_and_text(
    soup: BeautifulSoup, reference_dict: Dict[str, ContentReference]
):
    """Returns a tuple of id, text, reference pairs for all elements."""

    def recurse(element):
        """
        A recursive function that traverses the HTML elements and returns a list of tuples containing id, text, and reference pairs for all elements.
        """
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
    """
    Attaches content and references to a BeautifulSoup object based on a table of contents and a list of references.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object representing the HTML content.
        toc (List[ContentHierarchyNode]): The table of contents as a list of ContentHierarchyNode objects.
        references (List[ContentReference]): The list of references as ContentReference objects.

    Returns:
        None

    This function takes a BeautifulSoup object, a table of contents, and a list of references and attaches the content and references to the corresponding nodes in the table of contents. It does this by recursively traversing the HTML elements and identifying the relevant sections based on their IDs. It then adds the content and references to the corresponding nodes in the table of contents.

    The function first creates a dictionary of references using the href attribute as the key. It then calls the `recurse_ids_and_text` function to flatten the HTML content and retrieve the IDs, text, and references. It then flattens the table of contents using the `flatten_toc` function.

    The function iterates over the flattened text and references, and checks if the current ID matches the next ID in the table of contents. If it does, it adds the current content and references to the corresponding node in the table of contents and resets the current content and references. It then updates the current index and the next ID. If the current ID does not match the next ID, it appends the text and reference to the current content and references.

    After iterating over all the flattened text and references, the function adds the remaining content and references to the last node in the table of contents.

    Note: The function assumes that the table of contents is in the correct order and that there are no missing or extra nodes.

    """
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
