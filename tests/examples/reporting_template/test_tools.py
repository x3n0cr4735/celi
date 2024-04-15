import os
from dotenv import load_dotenv
from celi_framework.examples.reporting_template.tools import ReportingToolImplementations

# load_dotenv()

# def test_section_text_getter():
#     tools = ReportingtToolImplementations(os.environ["DOC_DIR"])
#     text = tools.section_text_getter('{"Example Document": "1"}')
#     assert text.strip().split("\n")[-1] == "<empty section>"
