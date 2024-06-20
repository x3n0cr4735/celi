# FastAPI that serves CELI documents
import asyncio
import inspect
import logging
import os
import uuid
from asyncio import Queue, Task
from dataclasses import asdict, dataclass
from typing import Dict, Optional, Tuple

from dotenv import load_dotenv
from fastapi import Body, FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket

from celi_framework.core.celi_update_callback import CELIUpdateCallback
from celi_framework.core.mt_factory import MasterTemplateFactory
from celi_framework.core.processor import ProcessRunner
from celi_framework.core.section_processor import SectionProcessor
from celi_framework.core.websocket.streams import (
    map_step,
    fastapi_websocket_text_sink,
    queue_source,
)
from celi_framework.logging_setup import setup_logging
from celi_framework.main import setup_standard_args, parse_standard_args
from celi_framework.utils.llm_cache import enable_llm_caching
from celi_framework.utils.utils import get_obj_by_name

logger = logging.getLogger(__name__)


@dataclass
class SessionData:
    """The server can have multiple active CELI sessions at once.  This is the data stored for each."""

    update_queue: Queue
    processor: ProcessRunner
    task: Task


setup_logging()
load_dotenv()

parser = setup_standard_args()
parser.add_argument(
    "--init_class",
    type=str,
    default=os.getenv("TOOL_INIT_CLASS"),
    help="Name of the class that will be used to initialize a session.",
)
args = parser.parse_args([])
init_class = get_obj_by_name(args.init_class)
celi_config = parse_standard_args(args)
if celi_config.llm_cache:
    enable_llm_caching()

current_sessions: Dict[str, SessionData] = {}

app = FastAPI()

# Add CORS middleware to allow connections from your React app domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for allowing all domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


logger.info("Completed server initialization")


@dataclass
class UpdateMessage:
    section: Optional[str]
    type: str  # Will be "message" / "output" / "completed"
    message: Optional[Dict[str, str] | Tuple[str, str]] = None
    output: Optional[str] = None


@dataclass
class QueueingCallback(CELIUpdateCallback):
    """Received updates from CELI and puts them into the queue for forwarding back to the client."""

    queue: Queue

    def on_message(self, section: str, msg: Dict[str, str] | Tuple[str, str]):
        try:
            loop = asyncio.get_event_loop()
            text = SectionProcessor.format_message_content(msg)
            loop.create_task(
                self.queue.put(UpdateMessage(section, "message", message=text))
            )
        except Exception as e:
            logger.exception(f"on_message error - {msg}")

    def on_section_complete(self, section: str):
        loop = asyncio.get_event_loop()
        loop.create_task(self.queue.put(UpdateMessage(section, "completed")))

    def on_output(self, section: str, output: str):
        loop = asyncio.get_event_loop()
        loop.create_task(
            self.queue.put(UpdateMessage(section, "output", output=output))
        )

    def on_all_sections_complete(self):
        pass


def _check_for_init_arg(cls, arg_name: str) -> bool:
    constructor = cls.__init__
    signature = inspect.signature(constructor)
    parameters = signature.parameters
    return arg_name in parameters


@app.post("/sessions/create")
async def sessions_create(data: dict = Body(...)) -> Dict[str, str]:
    """Starts a new CELI session with the given parameters."""
    init = init_class(**data)
    logger.info(
        f"Initializing {celi_config.job_description.tool_implementations_class} with {init}"
    )
    update_queue = Queue()
    cb = QueueingCallback(update_queue)

    # If the tool class accepts a callback, pass it in.
    tools_take_callback = _check_for_init_arg(
        celi_config.job_description.tool_implementations_class,
        "callback",
    )
    tool_implementations = celi_config.job_description.tool_implementations_class(
        **init.dict(), **{"callback": cb} if tools_take_callback else {}
    )
    mt = MasterTemplateFactory(
        job_desc=celi_config.job_description,
        schema=tool_implementations.get_schema(),
    )
    process_runner = ProcessRunner(
        master_template=mt,
        tool_implementations=tool_implementations,
        llm_cache=celi_config.llm_cache,
        primary_model_name=celi_config.primary_model_name,
        model_url=celi_config.model_url,
        max_tokens=celi_config.max_tokens,
        callback=cb,
    )
    task = asyncio.create_task(process_runner.run())
    # task = asyncio.create_task(dummy_task(cb))

    session_id = uuid.uuid4().hex
    current_sessions[session_id] = SessionData(
        update_queue=update_queue, processor=process_runner, task=task
    )
    return {"session_id": session_id}


async def dummy_task(cb: CELIUpdateCallback):
    for i in range(100):
        await asyncio.sleep(3)
        logger.info("Sending message")
        cb.on_message("1", {"message": "Hello!"})


@app.get("/session/{session_id}/schema")
async def get_schema(session_id: str) -> dict[str, str]:
    """This returns the schema of the CELI document."""
    return current_sessions[session_id].processor.get_schema()


@app.websocket("/session/{session_id}/updates")
async def send_updates(websocket: WebSocket, session_id: str):
    """Streams back call CELI updates."""
    session_data = current_sessions[session_id]
    outputs = queue_source(session_data.update_queue)
    outputs = map_step(outputs, lambda x: asdict(x))
    outputs = fastapi_websocket_text_sink(outputs, websocket)
    await asyncio.gather(outputs)


@dataclass
class HumanInput(BaseModel):
    section_id: str
    input: str


@app.post("/session/{session_id}/human_input")
async def human_input(session_id: str, input: HumanInput):
    """Redoes a particular section, providing the given human input to the process."""
    session_data = current_sessions[session_id]
    task = asyncio.create_task(
        session_data.processor.add_human_input_on_section(**input.dict())
    )
