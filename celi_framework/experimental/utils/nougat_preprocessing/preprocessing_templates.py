def make_complete_tables_1(section, section_content):
    formatted_prompt = f"""
I have an incomplete LaTeX table that I need help completing. The table is a part of the section '{section}' and contains data on various parameters. Some entries in the table are missing, and I would like your assistance in filling out these missing parts while maintaining the existing formatting and style.

Here's the incomplete LaTeX table:

{section_content}

Please complete the missing values and structure for the table. Where specific data is not available, please provide common or typical values based on standard practices. Ensure the table remains well-structured and retains its LaTeX formatting. Send back the original text but with the complete table.

If there was no incomplete table simply respond with "None".
    """
    return formatted_prompt


def make_parse_clean_tables_1(section, section_content):
    formatted_prompt = f"""I have a report. In section {section}, which content is below (see "SECTION"), I have one or more LaTeX tables. Could you help me identify the tables, and their headings (or 'Non-Titled' if they have no title - add 1,2,3.. or whatever order they are in in the section), and present each table in a well-structured format (if they are ill-structured, or incomplete, clean them up while keeping the original intended structure and content)? Keep the latex formatting. Give the result back in this format: {{section number: [{{TABLE TITLE: LATEX TABLE 1}}, {{TABLE TITLE: LATEX TABLE 2}}]}}. DO NOT GIVE ME BACK THE ORIGINAL TABLES. IF A SECTION LOOKS INCOMPLETE BECAUSE THERE IS AN UNFINISHED TABLE, COMPLETE THE TABLE AS BEST YOU CAN. IF YOU CANNOT FORMAT A TABLE BECAUSE IT'S INCOMPLETE OR TOO MESSED UP RETURN THIS IN THE LIST 'INCOMPLETE'.

DO NOT GIVE ME ANYTHING EXCEPT THE DICTIONARY I AM ASKING FOR. DO NOT ADD YOUR COMMENTS. DO NOT ADD YOUR THOUGHTS. DO NOT ADD YOUR SUGGESTIONS. 

Example ----

SECTION:
{section_content}
Response:
"""

    return formatted_prompt


def make_extract_table_data_1(response):
    formatted_prompt = f"""There is a list of one or more dictionaries in this text block. I want you to extract that list and print it out. If the text block starts with a brack and ends with a bracket (there is only a list) then just print it back with no changes.
    Text block: 
    {response}
    Return:
    """
    return formatted_prompt


def make_parse_clean_tables_2(section, section_content):
    formatted_prompt = f"""
I am compiling a report and require assistance with formatting the LaTeX tables present in section {section}. Below is the content of the mentioned section (refer to "SECTION"). The section may contain one or more LaTeX tables. PPlease help me identify these tables, extract their headings from the context and proximity of the table heading in the text, and restructure them if necessary to ensure they are well-formatted and complete. Retain the original LaTeX formatting. Provide the output in the following JSON-like format: 
LATEX TABLE 1 ||||||| LATEX TABLE 2 ||||||| LATEX TABLE N...
In case a table appears to be unfinished, attempt to complete it based on the existing structure and content. If a table cannot be formatted due to being overly incomplete or disorganized, include 'INCOMPLETE' as the value instead of the LaTeX table.

Ensure that the response only contains the requested dictionary, devoid of any additional comments, suggestions, or annotations.

Example ----

SECTION:
{section_content}

Response:
"""

    return formatted_prompt


def make_remove_table_syntax(section_content):
    formatted_prompt = f"""This is a text block from a multi markdown file that contains both regular text and latex tables (sometimes incomplete tables, just cutoff in the middle. I want you to remove any latex table syntax (keep the table heading, e.g. "Table 1 ..." and give me back the rest of the text with high fidelity of what was there originally. If there is no latex table content, just give me back the original text. DO NOT GIVE ME ANYTHING ELSE. NO COMMENTS. JUST THE TEXT I AM ASKING FOR. DO NOT REPHRASE, CLARIFY OR MODIFY THE NON-TABLE TEXT IN ANY WAY, SHAPE OR FORM (THIS INCLUDES TABLE HEADINGS).
    Text block: 
    {section_content}
    Return:
    """
    return formatted_prompt


def make_correct_mmd_output(section_content):
    formatted_prompt = f"""
Please make sure the sections of this document are separated properly as you see in the document. Make sure that no sections start on the same lines as previous ones. For example, in the following section 1.7.5 is mistakenly put into 1.7.4.4:

Example ---
##### 1.7.4.4 Review or Safety Boards

The Data Safety Monitoring Board reviewed safety data on a quarterly basis to ensure the ongoing safety of study participants.1.7.5 Other Evaluations

Should be:
##### 1.7.4.4 Review or Safety Boards

The Data Safety Monitoring Board reviewed safety data on a quarterly basis to ensure the ongoing safety of study participants.

#### 1.7.5 Other Evaluations

---

[Input Document]
{section_content}

Corrected Document:

"""
    return formatted_prompt
