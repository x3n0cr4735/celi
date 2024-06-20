import json
import logging
from dataclasses import dataclass
from json import JSONDecodeError
from typing import List, Dict, Tuple, Optional

from openai.types.chat.chat_completion import Choice

from celi_framework.core.celi_update_callback import CELIUpdateCallback
from celi_framework.core.job_description import ToolImplementations
from celi_framework.utils.llms import ToolDescription, ask_split
from celi_framework.utils.log import app_logger

logger = logging.getLogger(__name__)

ChatMessageable = Tuple[str, str] | Dict[str, str]

MAX_RETRIES = 2


@dataclass
class SectionProcessor:
    current_section: str
    system_message: str
    initial_user_message: str
    tool_descriptions: List[ToolDescription]
    tool_implementations: ToolImplementations
    primary_model_name: str
    llm_cache: bool
    monitor_instructions: str
    max_tokens: int
    callback: Optional[CELIUpdateCallback] = None
    model_url: Optional[str] = None

    def __post_init__(self):
        self.ongoing_chat: List[Dict[str, str] | Tuple[str, str]] = []
        self.pending_human_input = None
        self._update_ongoing_chat(("user", self.initial_user_message))
        self._update_ongoing_chat(
            (
                "user",
                f"Proceed to document section {self.current_section}, and do Task #1.",
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
            f"Started a new iteration for {self.current_section}.  Retry count is {self.retry_number}",
            extra={"color": "orange"},
        )
        self.section_complete_flag = False
        chat_len = len(self.ongoing_chat)

        llm_response = await ask_split(
            user_prompt=self.ongoing_chat,  # type: ignore
            model_name=self.primary_model_name,
            system_message=self.system_message,
            verbose=True,
            timeout=None,
            tool_descriptions=self.tool_descriptions,
            model_url=self.model_url,
            max_tokens=self.max_tokens,
        )
        self._update_ongoing_chat(
            ("assistant", str(llm_response.message.content or ""))
        )

        if llm_response.finish_reason == "tool_calls":
            tool_result = self.make_tool_calls(llm_response)
            [self._update_ongoing_chat(_) for _ in tool_result]

        app_logger.info(
            f"New chat iteration for {self.current_section}:\n"
            + self.format_chat_messages(self.ongoing_chat[chat_len:]),
            extra={"color": "green"},
        )

        if self.check_for_duplicates(self.ongoing_chat):
            logger.warning(
                f"Identified a loop in {self.current_section}.  Identical messages are repeating.  pop_context and moving on to the next section."
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
                    f"Proceed to document section {self.current_section}, and do Task #1",
                ),
            ]
            self.system_message = redo["new_system_message"]
            return True

    def check_for_duplicates(
        self, ongoing_chat: List[Dict[str, str] | Tuple[str, str]]
    ):
        if len(ongoing_chat) == 0:
            return False
        last_message = ongoing_chat[-1]
        duplicates = 0
        for message in ongoing_chat[:-1]:
            if message == last_message:
                duplicates += 1
        return duplicates > 2

    async def builtin_review(self):
        task_specific = (
            "Specifically, you should check for:\nself.monitor_instructions\n"
            if self.monitor_instructions
            else ""
        )
        system_message = f"""Your job is to review the chat history of an LLM trying to accomplish a goal and decide if
         it achieved that goal or if it should try again.  {task_specific}
         If it should try again, please propose a modified system and 
         initial user prompt that should be used.  Your output should be JSON that always contains a "success" tag and
         has the following format:
         If it did a good job:
            {{
                "rationale": "All requirements specified in the user_prompt were resolved.",
                "success": true,
            }}
        If it should try again:
            {{
                "rationale": "The output was not written before calling pop_context.",
                "success": false,
                "new_system_message": "The new system message to be used",
                "new_initial_user_message": "The new initial user message to be used"
            }}
        """
        user_message = f"The initial prompt was:\n{self.initial_user_message}\n\nHere is the chat history:\n{self.format_chat_messages(self.ongoing_chat)}\n\n"
        llm_response = await ask_split(
            user_prompt=user_message,  # type: ignore
            system_message=system_message,
            model_name=self.primary_model_name,
            verbose=True,
            timeout=None,
            json_mode=True,
            model_url=self.model_url,
            max_tokens=self.max_tokens,
        )
        text_response = llm_response.message.content.strip()

        logger.info(
            f"Output of final review for {self.current_section}:\n{text_response}"
        )
        if not text_response:
            logger.warning(
                f"Built-in review for {self.current_section} returned an empty response.  Assuming success."
            )
            return None

        try:
            ret = json.loads(text_response)
        except JSONDecodeError as e:
            logger.warning(
                f"Built-in review for {self.current_section} didn't return valid JSON.  {e}\nResponse was: {text_response}"
            )
            ret = {}

        if "success" not in ret:
            logger.warning(
                f"Built-in review for {self.current_section} didn't return a success key.  Assuming success."
            )
            return None

        if ret["success"]:
            return None

        if (
            "new_system_message"
            and "new_initial_user_message" not in ret
            or ret["new_system_message"] == self.system_message
        ):
            logger.warning(
                f"Built-in review for {self.current_section} didn't return a new_system_message or new_initial_user_message.  Skipping retry."
            )
            return None

        return ret

    @staticmethod
    def format_message_content(m: ChatMessageable):
        if isinstance(m, dict):
            return f"{m['role'].capitalize()}:\n{m['content']}"
        return f"{m[0].capitalize()}:\n{m[1]}"

    @staticmethod
    def format_chat_messages(msgs: List[ChatMessageable]):
        return "\n\n".join(SectionProcessor.format_message_content(m) for m in msgs)

    def make_tool_calls(self, response: Choice):
        def make_tool_call(tool_call):
            name = tool_call.function.name
            function_return = None
            try:
                arguments = json.loads(tool_call.function.arguments)
            except JSONDecodeError as e:
                arguments = "<Unable to parse>"
                function_return = f"Error: Unable to parse arguments {e}"
            if not function_return:
                if name == "pop_context":
                    # pop_context is a built-in function and not in the tool_implementations.
                    self.section_complete_flag = True
                    function_return = arguments["current_section_number"]
                else:
                    if hasattr(self.tool_implementations, name):
                        method_to_call = getattr(self.tool_implementations, name)
                        try:
                            function_return = method_to_call(**arguments)
                        except Exception as e:
                            function_return = f"Error: {e}"
                    else:
                        app_logger.error(
                            f"Unknown function name: {name}", extra={"color": "red"}
                        )
                        return (
                            "user",
                            f"Error: Called unknown function name: {name} with arguments {arguments}",
                        )
            function_log = f"Call to function {name} with arguments {arguments} returned\n{function_return}"
            return {"role": "function", "name": name, "content": function_log}

        return [make_tool_call(_) for _ in response.message.tool_calls]
