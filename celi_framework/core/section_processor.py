import inspect
import json
import logging
from dataclasses import dataclass
from json import JSONDecodeError
from typing import List, Dict, Tuple, Optional

from celi_framework.core.celi_update_callback import CELIUpdateCallback
from celi_framework.core.job_description import ToolImplementations
from celi_framework.utils.llm_response import LLMResponse
from celi_framework.utils.llms import ToolDescription, ask_split
from celi_framework.utils.log import app_logger
from celi_framework.utils.token_counters import TokenCounter

logger = logging.getLogger(__name__)

ChatMessageable = Tuple[str, str] | Dict[str, str]

MAX_RETRIES = 2


@dataclass
class SectionProcessor:
    """This is the core processor that uses iterative calls to LLMs to manage the drafting process.  Each
    SectionProcessor runs independently, working through a task list described in the JobDescription and using
    the tools it provides.
    """

    current_section: str
    system_message: str
    initial_user_message: str
    tool_descriptions: List[ToolDescription]
    tool_implementations: ToolImplementations
    primary_model_name: str
    llm_cache: bool
    monitor_instructions: str
    max_tokens: int
    force_tool_every_n: int
    callback: Optional[CELIUpdateCallback] = None
    model_url: Optional[str] = None
    token_counter: Optional[TokenCounter] = None

    def __post_init__(self):
        self.ongoing_chat: List[Dict[str, str] | Tuple[str, str]] = []
        self.pending_human_input = None
        self._update_ongoing_chat(("user", self.initial_user_message))
        self._update_ongoing_chat(
            (
                "user",
                f"You are working on section {self.current_section}.  Begin with Task #1.",
            )
        )
        self.section_complete_flag = False
        self.retry_number = 0
        self.tool_names = [_.name for _ in self.tool_descriptions]
        self.is_running = False

    def _update_ongoing_chat(self, msg: Dict[str, str] | Tuple[str, str]):
        self.ongoing_chat.append(msg)
        if self.callback:
            self.callback.on_message(self.current_section, msg)
        if self.pending_human_input:
            user_msg = ("user", self.pending_human_input)
            self.ongoing_chat.append(user_msg)
            self.callback.on_message(self.current_section, user_msg)
            self.pending_human_input = None

    async def add_human_input(self, input: str):
        if self.is_running:
            self.pending_human_input = input
        else:
            self._update_ongoing_chat(("user", input))
            # If we've finished, start again.
            await self.run()

    async def run(self):
        self.is_running = True
        while self.is_running:
            self.is_running = await self.process_iteration()
        if self.callback:
            self.callback.on_section_complete(self.current_section)

    async def process_iteration(self):
        """
        Run one iteration of the main execution loop for drafting documents.

        Within each iteration of the loop, the method performs the following operations:
            - Prepares a prompt for the language model based on the current conversation history.
            - Processes the language model's response, including handling any specified function calls, updating
                the draft content, and managing the ongoing conversation context.
            - Checks if the iteration is in a loop.
            - If the section is complete, call builtin_review to check the resul and decide whether a redo is required.

        Returns:
            True if the drafting is still in progress and another iteration should be run.  False if the process
            should stop.
        """
        app_logger.info(
            f"Started a new iteration for section {self.current_section}.  Retry count is {self.retry_number}",
        )
        self.section_complete_flag = False
        chat_len = len(self.ongoing_chat)

        n_since_tool_use = self.responses_since_last_tool_call(self.ongoing_chat)
        force_tool_use = n_since_tool_use >= self.force_tool_every_n
        if force_tool_use:
            logger.debug(
                f"Forcing tool use because there have been no tool calls in the last {n_since_tool_use} iterations."
            )

        llm_response = await ask_split(
            user_prompt=self.ongoing_chat,  # type: ignore
            model_name=self.primary_model_name,
            system_message=self.system_message,
            verbose=True,
            timeout=None,
            tool_descriptions=self.tool_descriptions,
            model_url=self.model_url,
            max_tokens=self.max_tokens,
            token_counter=self.token_counter,
            force_tool_use=force_tool_use,
        )
        self._update_ongoing_chat(("assistant", str(llm_response.content or "")))

        if llm_response.finish_reason == "tool_calls":
            tool_result = await self.make_tool_calls(llm_response)
            [self._update_ongoing_chat(_) for _ in tool_result]

        app_logger.info(
            f"LLM response for section {self.current_section}:\n"
            + self.format_chat_messages(self.ongoing_chat[chat_len:]),
            extra={"color": "green"},
        )

        if self.check_for_duplicates(self.ongoing_chat):
            logger.warning(
                f"Identified a loop of repeating message in section {self.current_section}.  Terminating this attempt."
            )
            self.section_complete_flag = True

        if not self.section_complete_flag:
            return True

        redo = await self.builtin_review()
        if not redo:
            return False
        else:
            if self.retry_number >= MAX_RETRIES:
                logger.warning(
                    f"Exhausted the maximum number of retries for {self.current_section}"
                )
                return False
            self.retry_number += 1
            logger.warning(f"Retrying section {self.current_section}")
            self.ongoing_chat = [
                ("user", redo["new_initial_user_message"]),
                (
                    "user",
                    f"You are working on section {self.current_section}.  Begin with Task #1.",
                ),
            ]
            self.system_message = redo["new_system_message"]
            return True

    @staticmethod
    def responses_since_last_tool_call(
        ongoing_chat: List[Dict[str, str] | Tuple[str, str]]
    ):
        ix = 0
        for m in reversed(ongoing_chat):
            role = m[0] if isinstance(m, tuple) else m["role"]
            if role == "function":
                break
            if role == "assistant":
                ix += 1
        return ix

    @staticmethod
    def check_for_duplicates(ongoing_chat: List[Dict[str, str] | Tuple[str, str]]):
        if len(ongoing_chat) == 0:
            return False
        last_message = ongoing_chat[-1]
        duplicates = 0
        for message in ongoing_chat[-6:-1]:
            if message == last_message:
                duplicates += 1
        if duplicates >= 5:
            return True
        # Check for cycles of 2 repeating messages
        if len(ongoing_chat) > 2:
            previous_message = ongoing_chat[-2]
            alternating_duplicates = 0
            if previous_message != last_message:
                for message in ongoing_chat[-7:-2]:
                    if message == previous_message:
                        alternating_duplicates += 1
                    if duplicates >= 2 and alternating_duplicates >= 2:
                        return True
        return False

    async def builtin_review(self):
        task_specific = (
            f"Specifically, you should check for:\n{self.monitor_instructions}\n"
            if self.monitor_instructions
            else ""
        )
        system_message = f"""Your job is to review the chat history of an LLM trying to accomplish a goal.  This first 
         thing you should do is find all the tool calls made by the LLM.  After you have done that, review those to 
         decide if the overall goal was achieved or if the LLM should try again.  Think step by step and explain your
         reasoning.  
         
         You can identify tool calls in the chat  history because they will look like this: 
         
         Function:
         Call to function run_tests with arguments....
         
         {task_specific}

         If the LLM should try again, please propose a modified system and 
         initial user prompt that should be used.  Your output should be JSON that always contains tags for
         "tool_calls_made", "ratioale", and "success".
         has the following format:
         Example of a successful review:
            {{
                "tool_calls_made": ['get_prompt', 'ask_question', 'save_draft_output', 'complete_section'],
                "rationale": "All requirements specified in the user_prompt were resolved.",
                "success": true,
            }}
         Example of a unsuccessful review:
            {{
                "tool_calls_made": ['get_prompt', 'complete_section'],
                "rationale": "save_draft_output was not called before calling complete_section.",
                "success": false,
                "new_system_message": "The new system message to be used",
                "new_initial_user_message": "The new initial user message to be used"
            }}
        """
        user_message = f"""The initial system message was\n<SystemMessage>{self.system_message}</SystemMessage>.  The
        initial user message was:\n<UserMessage>{self.initial_user_message}</UserMessage>\n\nHere is the chat history:
        {self.format_chat_messages(self.ongoing_chat)}"""
        # logger.debug(f"Built-in review input:\n{user_message}")
        llm_response = await ask_split(
            user_prompt=user_message,  # type: ignore
            system_message=system_message,
            model_name=self.primary_model_name,
            verbose=True,
            timeout=None,
            json_mode=True,
            model_url=self.model_url,
            max_tokens=self.max_tokens,
            token_counter=self.token_counter,
        )
        text_response = llm_response.content.strip()

        logger.info(
            f"Output of final review for section {self.current_section}:\n{text_response}"
        )
        if not text_response:
            logger.warning(
                f"Built-in review for section {self.current_section} returned an empty response.  Assuming success."
            )
            return None

        try:
            ret = json.loads(text_response)
        except JSONDecodeError as e:
            logger.warning(
                f"Built-in review for section {self.current_section} didn't return valid JSON.  {e}\n"
                f"Response was: {text_response}"
            )
            ret = {}

        if "success" not in ret:
            logger.warning(
                f"Built-in review for section {self.current_section} didn't return a success key.  Assuming success."
            )
            return None

        if ret["success"]:
            return None

        if "new_system_message" not in ret or "new_initial_user_message" not in ret:
            logger.warning(
                f"Built-in review for section {self.current_section} didn't return a new_system_message or "
                f"new_initial_user_message.  Skipping retry."
            )
            return None

        if (
            ret["new_system_message"] == self.system_message
            and ret["new_initial_user_message"] == self.initial_user_message
        ):
            logger.warning(
                f"Built-in review for section {self.current_section} didn't changeany messages.  Skipping retry."
            )
            return None

        return ret

    @staticmethod
    def format_message_content(m: ChatMessageable):
        if isinstance(m, dict):
            non_role = {k: v for k, v in m.items() if k != "role"}
            return f"{m['role'].capitalize()}:\n{non_role}"
        return f"{m[0].capitalize()}:\n{m[1]}"

    @staticmethod
    def format_chat_messages(msgs: List[ChatMessageable]):
        return "\n\n".join(SectionProcessor.format_message_content(m) for m in msgs)

    async def make_tool_calls(self, response: LLMResponse):
        async def make_tool_call(tool_call):
            name = tool_call.function.name
            function_return = None
            try:
                arguments = json.loads(tool_call.function.arguments)
            except JSONDecodeError as e:
                arguments = "<Unable to parse>"
                function_return = f"Error: Unable to parse arguments {e}"
            if not function_return:
                if name == "complete_section":
                    # conplete_section is a built-in function and not in the tool_implementations.
                    self.section_complete_flag = True
                    function_return = arguments["current_section_number"]
                else:
                    if hasattr(self.tool_implementations, name):
                        method_to_call = getattr(self.tool_implementations, name)
                        try:
                            function_return = method_to_call(**arguments)
                            if inspect.iscoroutine(function_return):
                                function_return = await function_return
                        except Exception as e:
                            function_return = f"Error: {e}"
                    else:
                        app_logger.warning(f"Unknown function name: {name}")
                        return (
                            "user",
                            f"Error: Called unknown function name: {name} with arguments {arguments}",
                        )
            return {
                "role": "function",
                "name": name,
                "id": tool_call.id,
                "arguments": tool_call.function.arguments,
                "return_value": str(function_return),
                "is_error": isinstance(function_return, str)
                and function_return.startswith("Error"),
            }

        return [await make_tool_call(_) for _ in response.tool_calls]
