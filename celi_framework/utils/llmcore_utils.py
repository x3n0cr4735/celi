"""
The `utils.llmcore_utils` module serves as a comprehensive toolkit for leveraging Large Language Models (LLMs)
such as OpenAI's models and LLaMA CPP for natural language processing tasks within a broader application context.
This module integrates core components from the `llm_core` library, providing functionality for parsing textual
messages, conducting error analysis, performing secondary analysis, generating dense summaries, and processing
content through specialized LLM assistants.

Features:
- Data class definitions for structured representation of messages, errors, function returns, analysis reports,
  and output summaries, enabling type-safe operations and clarity in data handling.
- Utility functions for parsing textual inputs into structured data classes using OpenAI's and LLaMA CPP's parsers,
  facilitating the extraction of meaningful information from free-text responses.
- Integration with MongoDB for data persistence, demonstrating how LLM outputs can be stored, retrieved, and processed
  for applications requiring database interactions.
- Implementation of question-answering workflows and content verification methods that employ LLMs to validate,
  analyze, and enhance textual content based on specific criteria such as relevance, accuracy, and clarity.
- Techniques for reducing hallucinations and improving the reliability of LLM responses through the Chain of Verification
  (CoV) and summarization strategies aimed at condensing extensive content into more manageable forms.

Usage:
This module is designed to be utilized in applications that require sophisticated text processing capabilities,
including but not limited to content creation, document analysis, error detection in automated outputs,
and the generation of actionable insights from unstructured data. It exemplifies the integration of LLMs
into practical workflows, offering a blend of parsing, summarization, and content enhancement utilities
that can be adapted to various domains and use cases.

Dependencies:
- llm_core: A library providing core functionalities for interacting with LLMs.
- dotenv: For loading environment variables that may include API keys or database connection strings.
- requests: Used for making HTTP requests to external services, particularly when interacting with LLM APIs.
- dataclasses: For defining structured data types that facilitate the organization and manipulation of complex data.

Note:
- The module includes placeholders and TODO comments indicating areas where customization and further development
  are required to adapt the utilities to specific application needs or to integrate with different LLMs and databases.

Examples:
- Parsing structured data from LLM responses for document analysis tasks.
- Conducting secondary analysis on textual content to assess its quality and relevance.
- Generating dense summaries of extensive articles or reports to extract key insights.
"""

import codecs
from dataclasses import asdict, dataclass, field
import json
from typing import Callable, List, Optional, Type, TypeVar

from llm_core.llm.base import LLMBase, ChatCompletion
from llm_core.parsers import BaseParser
from llm_core.settings import MODELS_CACHE_DIR

from celi_framework.utils.codex import MongoDBUtilitySingleton
from celi_framework.utils.log import app_logger
from celi_framework.utils.utils import UnrecoverableException

# TODO -> This seems to be the way to do CoV with GPT 3.5 :
#   https://advanced-stack.com/resources/how-to-reduce-hallucinations-using-chain-of-verification-cov-in-large-language-models.html

# LLAMACPP_MODEL_SMALL = "mistral-7b-instruct-v0.1.Q5_K_M.gguf"
# LLAMACPP_MODEL_BIG = "mixtral-8x7b-v0.1.Q5_K_M.gguf"
# OPENAI_MODEL = "gpt-3.5-turbo-16k"


@dataclass
class IsPromptError:
    is_there_a_function_exception: bool
    is_there_a_function_error: bool


@dataclass
class FunctionReturn:
    name: str
    arguments: dict
    return_msg: str


@dataclass
class SecondaryAnalysisReport:
    relevance: int
    accuracy: int
    completeness: int
    clarity: int
    integration: int
    contextual_sufficiency: int
    overall_quality: int
    strengths: List[str] = field(default_factory=list)
    areas_for_improvement: List[str] = field(default_factory=list)
    contextual_evaluation: str = ""
    suggestions_for_current_task: List[str] = field(default_factory=list)
    suggestions_for_future_tasks: List[str] = field(default_factory=list)


@dataclass
class FinalOutput:
    doc_section: str
    draft: str
    comments: str
    success_flag: str
    source_mapping: str
    scope_of_section: str
    tables: List[str] = field(default_factory=list)
    figures: List[str] = field(default_factory=list)
    cross_references: List[str] = field(default_factory=list)


def patch_llm_core(llm: LLMBase):
    """llm_core ignores history when  calculating the context size for parsing.
    This function monkey-patches and LLMBase object.
     It can be removed once this PR is merged and celi is upgraded to a new version of llm-core.
    PR: https://github.com/advanced-stack/py-llm-core/pull/12
    """

    def patched_sanitize_prompt(
        self,
        prompt,
        history=None,
        schema=None,
    ):
        schema_prompt = ""

        if schema:
            schema_prompt = json.dumps(schema)

        complete_prompt = [
            self.system_prompt,
            prompt,
            str(history) if history else "",
            schema_prompt,
        ]

        complete_prompt = "\n".join(complete_prompt)

        required_ctx_size = len(codecs.encode(complete_prompt, self.name))
        if required_ctx_size > self.ctx_size:
            raise OverflowError(
                f"Prompt too large {required_ctx_size} for this model {self.ctx_size}"
            )

        return self.ctx_size - required_ctx_size

    llm.sanitize_prompt = patched_sanitize_prompt.__get__(llm, llm.__class__)


def cache_llm_core_model(llm: LLMBase, codex: MongoDBUtilitySingleton):
    """
    Monkey patch an existing LLM class to provide caching.  This seems to be the easiest way to handle this in LLM core.
    """

    def cached_ask(self, prompt, history, **kwargs):
        result = codex.check_llm_cache(
            cls_name=str(type(llm)),
            model=self.name,
            prompt=prompt,
            history=history,
            **kwargs,
        )
        if result:
            app_logger.debug("Using cached LLM response")
            return ChatCompletion.parse(result["completion"])
        else:
            result = type(llm).ask(self, prompt=prompt, history=history, **kwargs)
            codex.cache_llm_response(
                response={"completion": asdict(result)},
                cls_name=str(type(llm)),
                model=self.name,
                prompt=prompt,
                history=history,
                **kwargs,
            )
            return result

    llm.ask = cached_ask.__get__(llm, llm.__class__)


T = TypeVar("T")
ParserFactory = Callable[[Type], BaseParser]


def new_parser_factory(
    parser_cls: Type,
    model: str,
    cache: bool = False,
    codex: Optional[MongoDBUtilitySingleton] = None,
) -> ParserFactory:
    """
    Creates a parser that uses a particular model.
    """
    assert codex or not cache, "You must provide a codex to cache the parser."

    def create_parser(target_cls) -> BaseParser:
        ret = parser_cls(model=model, target_cls=target_cls)
        patch_llm_core(ret.model_wrapper)
        if cache:
            cache_llm_core_model(ret.model_wrapper, codex)  # type: ignore
        return ret

    return create_parser


def parse(dataclass_parser: ParserFactory, target_cls: Type[T], msg: str) -> T:
    """
    Parses the given message into the specified target_cls, using the model defined by parser_factory.
    """
    try:
        with dataclass_parser(target_cls) as parser:
            ret = parser.parse(msg)  # type: ignore
            app_logger.info(f"Parsed {ret}")
            setattr(ret, "parser_model", parser.model_name)
            return ret
    except ValueError as e:
        if "Model path does not exist" in str(e):
            raise UnrecoverableException(
                f"Model has not been cached.  Download with something like\nwget -P {MODELS_CACHE_DIR} https://huggingface.co/TheBloke/Mixtral-8x7B-v0.1-GGUF/resolve/main/mixtral-8x7b-v0.1.Q2_K.gguf\n",
                e,
            )
        else:
            raise e


# @dataclass
# class DenseSummary:
#     denser_summary: str
#     missing_entities: List[str]


# @dataclass
# class DenserSummaryCollection:
#     summaries: List[DenseSummary]


# def parse_message_with_openai_parser(msg: str) -> Message:
#     """
#     Parses a given message string into a Message object using OpenAIParser.

#     Args:
#         msg (str): The message string to be parsed.

#     Returns:
#         Message: An instance of the Message data class containing the parsed data.
#     """
#     # TODO -> Implement using chunkify!!!
#     with OpenAIParser(
#         Message, model=OPENAI_MODEL
#     ) as parser:  # OpenAIParser(Message, model=OPENAI_MODEL)
#         message = parser.parse(msg)
#     return message


# @add_parser_model(LLAMACPP_MODEL_BIG, Message)
# @time_it
# def parse_message_with_llamacpp_parser(msg: str) -> Message:
#     """
#     Parses a given message string into a Message object using OpenAIParser.

#     Args:
#         msg (str): The message string to be parsed.

#     Returns:
#         Message: An instance of the Message data class containing the parsed data.
#     """
#     # TODO -> Implement chunkify utilization
#     with LLaMACPPParser(
#         Message, model=LLAMACPP_MODEL_BIG
#     ) as parser:  # OpenAIParser(Message, model=OPENAI_MODEL)
#         message = parser.parse(msg)
#     return message


# #     model = LLAMACPP_MODEL
# #     # model = "gpt-3.5-turbo"
# #     assistant_cls = LLaMACPPAssistant


# def parse_completion_for_error_with_openai_parser(msg: str) -> IsPromptError:
#     """
#     Parses a given message string into a Message object using OpenAIParser.

#     Args:
#         msg (str): The message string to be parsed.

#     Returns:
#         Message: An instance of the Message data class containing the parsed data.
#     """
#     model = OPENAI_MODEL
#     msg = get_first_chunk(model=model, content=msg, chunk_size=14_000)
#     with OpenAIParser(IsPromptError, model=model) as parser:
#         message = parser.parse(msg)
#     return message


# @add_parser_model(LLAMACPP_MODEL_SMALL, IsPromptError)
# @time_it
# def parse_completion_for_error_with_llamacpp_parser(msg: str) -> IsPromptError:
#     """
#     Parses a given message string into a Message object using OpenAIParser.

#     Args:
#         msg (str): The message string to be parsed.

#     Returns:
#         Message: An instance of the Message data class containing the parsed data.
#     """
#     model = OPENAI_MODEL
#     msg = get_first_chunk(model=model, content=msg, chunk_size=3_000)
#     with LLaMACPPParser(IsPromptError, model=LLAMACPP_MODEL_SMALL) as parser:
#         message = parser.parse(msg)
#     return message


# def check_prompt_completion_for_errors(text, model=LLAMACPP_MODEL, chunk_size=3000):
#     """
#     Splits the prompt completion into chunks and parses each chunk to check for errors or exceptions.
#     """
#     # Initialize the TokenSplitter with appropriate model and chunk size
#     splitter = TokenSplitter(model=model, chunk_size=chunk_size, chunk_overlap=100)  # Adjust parameters as needed
#
#     # Log the initial prompt completion for debugging purposes
#     print(f"Self.prompt_completion = {text[0:50]}...")
#
#     # Initialize a flag to track the presence of errors or exceptions
#     prompt_exception = False
#
#     # Iterate through chunks generated by TokenSplitter
#     for chunk in splitter.chunkify(text):
#         print(f"Processing chunk: {chunk[:50]}...")  # Log the start of a chunk for reference
#
#         # Parse the current chunk for errors or exceptions
#         parsed_prompt = parse_completion_for_error_with_llamacpp_parser(chunk)
#
#         # Check if the parsed result indicates an error or exception
#         if parsed_prompt.is_there_an_exception or parsed_prompt.is_there_an_error:
#             prompt_exception = True
#             print("Error or exception detected in prompt completion.")
#
#     return prompt_exception


# def parse_secondary_anylsis_with_openai_parser(msg: str) -> SecondaryAnalysisReport:
#     """
#     Parses a given message string into a Message object using OpenAIParser.

#     Args:
#         msg (str): The message string to be parsed.

#     Returns:
#         Message: An instance of the Message data class containing the parsed data.
#     """
#     # TODO -> Implement utlization of chunkify!!!
#     with OpenAIParser(SecondaryAnalysisReport, model=OPENAI_MODEL) as parser:
#         message = parser.parse(msg)
#     return message


# @add_parser_model(LLAMACPP_MODEL_BIG, SecondaryAnalysisReport)
# @time_it
# def parse_secondary_anylsis_with_llamacpp_parser(msg: str) -> SecondaryAnalysisReport:
#     """
#     Parses a given message string into a Message object using OpenAIParser.

#     Args:
#         msg (str): The message string to be parsed.

#     Returns:
#         Message: An instance of the Message data class containing the parsed data.
#     """
#     with LLaMACPPParser(SecondaryAnalysisReport, model=LLAMACPP_MODEL_BIG) as parser:
#         message = parser.parse(msg)
#     return message


# def parse_final_output_with_openai_parser(msg: str) -> FinalOutput:
#     """
#     Parses a given message string into a Message object using OpenAIParser.

#     Args:
#         msg (str): The message string to be parsed.

#     Returns:
#         Message: An instance of the Message data class containing the parsed data.
#     """
#     with OpenAIParser(FinalOutput, model="gpt-4-1106-preview") as parser:
#         message = parser.parse(msg)
#     return message


# @add_parser_model(LLAMACPP_MODEL_BIG, FinalOutput)
# @time_it
# def parse_final_output_with_llamacpp_parser(msg: str) -> FinalOutput:
#     """
#     Parses a given message string into a Message object using OpenAIParser.

#     Args:
#         msg (str): The message string to be parsed.

#     Returns:
#         Message: An instance of the Message data class containing the parsed data.
#     """
#     # TODO -> Use chunkify!!!
#     with LLaMACPPParser(FinalOutput, model=LLAMACPP_MODEL_BIG) as parser:
#         message = parser.parse(msg)
#     return message


# def process_q_a_content(model: str, assistant_cls, content: str, query: str):
#     analyst = Analyst(model, assistant_cls)
#     doubter = Doubter(model, assistant_cls)
#     verifier = ConsistencyVerifier(model, assistant_cls)

#     context = get_first_chunk(model, content)

#     analyst_response = analyst.ask(query, context)
#     print(analyst_response.content)

#     question_collection = doubter.verify(query, analyst_response.content)
#     questions = question_collection.questions
#     print(questions)

#     answers = []

#     for question in questions:
#         response = analyst.ask(question, context=context)
#         answers.append(response.content)

#     for question, answer in zip(questions, answers):
#         verifications = verifier.verify(
#             question=question, context=context, answer=answer
#         )
#         print(question, answer, verifications)


# def process_message_content(
#     model: str, assistant_cls, content: str, task: str, rsp_msg: str
# ):
#     """
#     Processes the given content by verifying the response to a specified task using language model assistants.

#     This function takes a piece of content along with a task and its response. It then generates questions
#     to validate the response, seeks answers to these questions, and finally verifies the consistency
#     and correctness of the answers against the original content and task response.

#     Args:
#         model (str): The model identifier used for processing content. Specifies which language model to use.
#         assistant_cls: The class of assistant to be used. This parameter determines which type of language model assistant
#                        (e.g., Analyst, Doubter, ConsistencyVerifier) is utilized for processing.
#         content (str): The text content that serves as the context for generating questions and verifying responses.
#         task (str): The specific task for which the response is being verified.
#         rsp_msg (str): The response message to the task that needs to be verified.

#     Returns:
#         None. However, the function prints out the questions generated for verification, the answers to these
#         questions, and the results of the verification process.
#     """

#     # Initialize instances of the language model assistants with the specified model and assistant class.
#     analyst = Analyst(model, assistant_cls)
#     doubter = Doubter(model, assistant_cls)
#     verifier = ConsistencyVerifier(model, assistant_cls)

#     # Use a TokenSplitter to chunk the content into manageable parts, if necessary.
#     context = get_first_chunk(model, content, chunk_size=14_000)

#     # Use the Doubter assistant to generate questions aimed at verifying the response to the task.
#     question_collection = doubter.verify(task, rsp_msg)
#     questions = question_collection.questions
#     # Print the questions to be used for verification.
#     print(questions)

#     answers = []  # Initialize a list to store answers to the generated questions.

#     # Iterate over the generated questions to obtain answers from the Analyst assistant.
#     for question in questions:
#         response = analyst.ask(question, context=context)
#         answers.append(
#             response.content
#         )  # Store the obtained answers for later verification.

#     # Iterate over each question-answer pair to verify the answers using the ConsistencyVerifier assistant.
#     for question, answer in zip(questions, answers):
#         verifications = verifier.verify(
#             question=question, context=context, answer=answer
#         )
#         # Print the question, its answer, and the verification result to provide insight into the verification process.
#         print(question, answer, verifications)


# def process_function_return(
#     model: str, assistant_cls, content: str, task: str, rsp_msg: str
# ):
#     return "To be completed"


# @staticmethod
# def summarize(
#     article: str, model="gpt-4", steps=5, initial_summary_length=80
# ) -> "DenserSummaryCollection":
#     """
#     Implement Chain of Density prompting with GPT-4 or similar models.

#     Args:
#         article (str): The article text to summarize.
#         model (str): Model identifier for the LLM.
#         steps (int): Number of iterations for density increment.
#         initial_summary_length (int): Word count for the initial summary.

#     Returns:
#         DenserSummaryCollection: A collection of increasingly dense summaries.
#     """
#     # Placeholder for OpenAIAssistant processing logic.
#     # Adapt this to your environment and the specific library/API you're using.
#     # The following is a conceptual structure:
#     summaries = []
#     for step in range(steps):
#         # Implement the call to your LLM here, adjusting the prompt according to your requirements
#         # and the specifics of how your LLM is accessed.
#         pass
#     return DenserSummaryCollection(summaries=summaries)


# # TODO -> Move to utils.utils?
# def get_first_chunk(model, content, chunk_size=3_000):
#     splitter = TokenSplitter(model=model, chunk_size=chunk_size)
#     context = splitter.first_extract(content)
#     return context


# # TODO -> Move to utils.utils?
# def chunkify_text(text: str, chunk_size: int = 10000) -> str:
#     """
#     Splits the text to fit the window size of a language model.

#     Args:
#         text (str): The text to be chunkified.
#         chunk_size (int): The maximum chunk size in tokens.

#     Returns:
#         str: The first chunk of the text.
#     """
#     splitter = TokenSplitter(chunk_size=chunk_size, chunk_overlap=0)
#     return next(splitter.chunkify(text))


# def process_content_from_document(
#     mongo_utility, collection_name, document_id, model, assistant_cls
# ):  # TODO -> How are we going to get the documentID
#     """
#     Fetches a document by its ID, extracts necessary attributes, and processes the message content.

#     Args:
#         mongo_utility (MongoDBUtilitySingleton): An instance of MongoDBUtilitySingleton for database operations.
#         collection_name (str): The name of the MongoDB collection.
#         document_id (str): The unique identifier of the document.
#         model (str): The model identifier used for processing content.
#         assistant_cls: The class of the assistant to be used for processing.

#     Returns:
#         None. The function primarily acts by calling process_message_content with the extracted attributes.
#     """
#     # Step 1: Fetch the document
#     document = mongo_utility.get_document_by_id(document_id, collection_name)

#     if not document:
#         print("Document not found.")
#         return

#     # Step 2: Extract attributes and prepare arguments for process_message_content
#     if "function_name" in document and document["function_name"]:
#         # Document represents a function return
#         attributes = mongo_utility.extract_function_return_attributes(document)
#         content = attributes.get("function_return", "")
#         task = (
#             attributes.get("function_name", "") + "\n" + attributes.get("arguments", "")
#         )
#         rsp_msg = attributes.get("return_msg", "")  # Adjusted to use 'return_msg'
#     else:
#         # Document represents a prompt completion
#         attributes = mongo_utility.extract_prompt_completion_attributes(document)
#         content = attributes.get("prompt_completion", "")
#         task = ""  # Define how to extract 'task' if needed
#         rsp_msg = attributes.get("response_msg", "")

#     # Step 3: Call process_message_content with extracted attributes #
#     process_message_content(model, assistant_cls, content, task, rsp_msg)
