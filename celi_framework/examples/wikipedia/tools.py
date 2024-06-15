import json
import logging
import re
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from llama_index.core.base.response.schema import Response
from llama_index.core.schema import MetadataMode, QueryBundle, NodeWithScore, TextNode
from llama_index.vector_stores.chroma.base import ChromaVectorStore
from pydantic import BaseModel

from celi_framework.core.celi_update_callback import CELIUpdateCallback
from celi_framework.core.job_description import BaseDocToolImplementations
from celi_framework.examples.wikipedia.index import get_wikipedia_index
from celi_framework.experimental.codex import MongoDBUtilitySingleton
from celi_framework.utils.llm_cache import get_celi_llm_cache
from celi_framework.utils.utils import format_toc, get_section_context_as_text

logger = logging.getLogger(__name__)


@dataclass
class RecreatedNode:
    """This is a recreated node, not an original one from the vector store.  Used to distinguish it from real TextNodes."""

    node_id: str
    metadata: Dict[str, Any]
    text: str

    def get_content(self):
        return self.text


class WikipediaInit(BaseModel):
    example_url: str
    target_url: str
    ignore_updates: bool = False


@dataclass
class WikipediaToolImplementations(BaseDocToolImplementations):
    """If ignore_updates is set, then a cached version of that URL will be used, even if it is out of date.
    Otherwise, a cache will only be used if it hasn't expired and the content hasn't changed.
    """

    example_url: str
    target_url: str
    ignore_updates: bool = False

    def __init__(
        self,
        example_url: str,
        target_url: str,
        ignore_updates: bool,
        drafts_dir: str = "target/celi_output/drafts",
        callback: Optional[CELIUpdateCallback] = None,
    ):
        super().__init__(drafts_dir=drafts_dir, callback=callback)
        self.example_url = example_url
        self.target_url = target_url
        self.ignore_updates = ignore_updates
        self.__post_init__()

    def __post_init__(self):
        self.example_page = self._page_title(self.example_url)
        self.target_page = self._page_title(self.target_url)
        self.example_index = get_wikipedia_index(
            self.example_url, ignore_updates=self.ignore_updates
        )
        # For the target, we only get references, not the actual content.
        self.target_index = get_wikipedia_index(
            self.target_url, include_content=False, ignore_updates=self.ignore_updates
        )
        self.target_query_engine = self.target_index.as_query_engine()
        self.target_retriever = self.target_index.as_retriever()
        if isinstance(self.example_index.vector_store, ChromaVectorStore):
            example_metas = self.example_index.vector_store._collection.get(
                include=["metadatas"]
            )
            self.example_meta_dict = dict(
                zip(example_metas["ids"], example_metas["metadatas"])
            )
        self.schema = WikipediaToolImplementations._extract_schema(
            self.example_index, self.example_meta_dict
        )

    # Retrieves the top level schema for the doc.  Ignore subsections as they change page to page.
    def get_schema(self) -> Dict[str, str]:
        return {k: v for k, v in self.schema.items() if "." not in k}

    def _page_title(self, url):
        return url.split("/")[-1].replace("_", " ")

    def get_example_and_target_names(self):
        """
        Gets the names for the example and target documents.  This way you can know what the target document is supposed to be about.
        """
        return {
            "example": self.example_page,
            "target": self.target_page,
        }

    def get_example_toc(self):
        """
        Retrieves and formats the table of contents for example document.

        Returns:
            str: A string containing the formatted table of contents for the example document.
        """
        return f"Table of Contexts:\n\n{format_toc(self.schema)}"

    def get_text_for_sections(
        self,
        sections_dict_str: str,
    ):
        """
        Extracts text from specified sections of documents.
        It handles different document types and logs any errors or warnings encountered.
        Returns concatenated text from the specified sections of the documents.
        If there is no content for the section, <empty section> will be returned.

        If the response contains "Error:", then there was a problem with the function call.

        Args:
            sections_dict_str (str): A JSON string mapping document names to their respective section numbers.  The json string will have the documents and sections in a dictionary.  The sections values should correspond to an entry in the table of contents for the specified document.
        """

        try:
            sections_dict = json.loads(sections_dict_str)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}", extra={"color": "red"})
            return "Error: Provided sections_dict_str is not a valid JSON format."

        output_text = ""
        for document_name, section_numbers in sections_dict.items():
            logger.info(
                f"Processing document: {document_name} with Sections: {section_numbers}",
                extra={"color": "cyan"},
            )
            # Load the document based on the document name
            if (
                document_name == "Example Document"
                or document_name == "example"
                or document_name == self.example_page
            ):
                sections = [
                    self._find_example_section_nodes(section_number)
                    for section_number in section_numbers
                ]
                for section_number, section in zip(section_numbers, sections):
                    text = " ".join(_.get_content() for _ in section).strip()
                    if (
                        not text
                        or text == ""
                        or len(section) == 0
                        or (text[:-1] == section[0].metadata["title"])
                    ):
                        text = "<empty section>"
                    output_text += (
                        f"{document_name} Section {section_number}:\n"
                        f"{get_section_context_as_text(section_number, self.schema)}"
                        f"Content:\n{text}\n"
                    )
            elif document_name in self.example_index.docstore.docs:
                document = self.example_index.docstore.docs[document_name]
                output_text += f"{document.get_content()}\n\n"
            else:
                err_msg = f"Error: No document named {document_name} was found to extract text from"
                logger.error(err_msg, extra={"color": "red"})
                output_text += f"{err_msg}\n\n"
                continue
        return output_text

    def get_corresponding_target_references_for_example_sections(
        self,
        section_numbers: List[str],
    ):
        """
        Given a list of section numbers from the example document, this function retrieves the references for the target document that are most similar to
        the example document references related to these sections.

        Args:
            section_numbers (List[str]): A list of section numbers from the example document.
        """
        reference_ids = list(
            self._get_references_for_example_sections(section_numbers).keys()
        )
        return self._get_corresponding_target_references(reference_ids)

    def _get_references_for_example_sections(self, section_numbers: List[str]):
        """
        Identify the documents that are referenced from the example document section.  It's returned as a dictionary of name to titles.

        Args:
            section_number (str): The section number document for which you want to get the example material.
        """

        def get_metadata_for_id(id):
            return (
                self.example_meta_dict[id]
                if isinstance(self.example_index.vector_store, ChromaVectorStore)
                else self.example_index.docstore.docs[id].metadata
            )

        return {
            id: get_metadata_for_id(id)["celi_reference_name"]
            for section_number in section_numbers
            for section in self._find_example_section_nodes(section_number)
            for id in section.metadata["celi_references_node_ids"].split(",")
            if len(id) > 0
        }

    def _get_corresponding_target_references(self, example_references: List[str]):
        """
        Given a list of references in the example document, search the target references to find the most closely related references.
        Returns a list of strings, each of which is a chunk of reference document.

        Args:
            example_references (str): A list of ids for the references in the example document.
        """

        def get_target_references(ref):
            if isinstance(self.example_index.vector_store, ChromaVectorStore):
                query = ""
                query_embedding = self.example_index.vector_store._collection.get(
                    ref, include=["embeddings"]
                )["embeddings"][0]
            else:
                if ref not in self.example_index.docstore.docs:
                    raise ValueError(f"Id {ref} was not an id of a example reference.")
                query_node = self.example_index.docstore.get_node(ref)
                query = query_node.get_content(MetadataMode.LLM)
                query_embedding = None

            related_nodes = self.target_retriever.retrieve(
                QueryBundle(query, embedding=query_embedding)
            )
            return related_nodes

        all_nodes = [
            node for ref in example_references for node in get_target_references(ref)
        ]
        TOP_N = 10
        logger.debug(
            f"Identified {len(all_nodes)} related nodes from {len(example_references)} reference nodes.  Keeping the top {TOP_N}."
        )
        top_nodes = self._get_top_nodes(all_nodes, TOP_N)

        def normalize_whitespace(s):
            return re.sub(r"\s+", " ", s)

        return "\n\n".join(
            normalize_whitespace(node.get_content()) for node in top_nodes
        )

    def _get_top_nodes(self, all_nodes: List[NodeWithScore], top_n: int):
        node_scores = {}
        for node in all_nodes:
            score = node_scores.get(node.node.node_id, 0.0)
            score += node.score
            node_scores[node.node.node_id] = score

        if len(node_scores) <= top_n:
            return all_nodes

        cutoff_score = sorted(list(node_scores.values()), reverse=True)[:top_n][-1]
        node_dict = {node.node_id: node for node in all_nodes}
        top_nodes = [
            node_dict[node_id]
            for node_id, score in node_scores.items()
            if score >= cutoff_score
        ]
        return top_nodes

    async def ask_question_about_target(self, prompt: str):
        """
        Ask a natural language question about the target subject and get a response.  This can be used to fill in gaps that are not present in the references.

        Args:
            prompt (str): The question to ask.
        """
        result = await get_celi_llm_cache().check_llm_cache(
            target_url=self.target_url, prompt=prompt
        )
        if result:
            logger.debug("Using cached LLM response")
            return self._dict_to_response(result["response"])

        else:
            logger.debug("Caching LLM response")
            result = self.target_query_engine.query(prompt)
            result_dict = self._response_to_dict(result)
            await self._get_codex().cache_llm_response(
                response={"response": result_dict},
                target_url=self.target_url,
                prompt=prompt,
            )
            # Convert back to a response just as a check that serialization was successful.
            ret = self._dict_to_response(result_dict)
            assert result == ret
            return ret

    def _response_to_dict(self, response: Response):
        ret = asdict(response)
        ret["source_nodes"] = [_.dict() for _ in response.source_nodes]
        return ret

    def _dict_to_response(self, d: Dict[str, Any]):
        d["source_nodes"] = [
            NodeWithScore(node=TextNode(**_["node"]), score=_["score"])
            for _ in d["source_nodes"]
        ]
        return Response(**d)

    def _get_codex(self):
        if not hasattr(self, "codex"):
            self.codex = MongoDBUtilitySingleton.get_instance()
        return self.codex

    @classmethod
    def _extract_schema(
        cls, index, meta_dict: Optional[Dict[str, Dict[str, Any]]] = None
    ):
        if isinstance(index.vector_store, ChromaVectorStore):
            all_metas = (
                meta_dict.values()
                if meta_dict
                else index.vector_store._collection.get(include=["metadatas"])[
                    "metadatas"
                ]
            )
            schema = {
                _["celi_section_number"]: _["title"]
                for _ in all_metas
                if "celi_section_number" in _
            }

            def section_key(section):
                return tuple(map(int, section.split(".")))

            schema = dict(sorted(schema.items(), key=lambda x: section_key(x[0])))
        else:
            schema = {
                _.metadata["celi_section_number"]: _.metadata["title"]
                for _ in index.docstore.docs.values()
                if "celi_section_number" in _.metadata
            }
        return schema

    def _find_example_section_nodes(self, section_number: str):
        if isinstance(self.example_index.vector_store, ChromaVectorStore):
            section_ids = [
                id
                for id, metadata in self.example_meta_dict.items()
                if metadata.get("celi_section_number", None) == section_number
            ]
            if len(section_ids) == 0:
                # Return an empty list here.  Otherwise, ._collection.get will return all the nodes.
                return []
            full = self.example_index.vector_store._collection.get(
                ids=section_ids, include=["metadatas", "documents"]
            )
            by_node = zip(full["ids"], full["metadatas"], full["documents"])
            by_node = sorted(by_node, key=lambda x: x[1]["celi_chunk_index"])
            return [
                RecreatedNode(node_id=id, metadata=metadata, text=doc)
                for id, metadata, doc in by_node
            ]
        else:
            try:
                return [
                    _
                    for _ in self.example_index.docstore.docs.values()
                    if _.metadata.get("celi_section_number", None) == section_number
                ]
            except IndexError:
                raise ValueError(f"Example section {section_number} not found.")
