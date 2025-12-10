from google.genai import types
from pydantic import BaseModel
repos = [
	{
        "link": "https://github.com/muhammadabdullahwarraich/slowapi.git",
        "include_exts": [".py"]
    },
    # {
	#     "link": "https://github.com/muhammadabdullahwarraich/coroutines-library.git",
    #     "include_exts": [".c"]
    # }
]
class Prompt2Model(BaseModel):
    suggestion: str
class Prompt:
    def __init__(self, id: str, ptext, gemini_config=None, output_parser=lambda x: x):
        self.id = id
        self.ptext = ptext
        self.gemini_config=gemini_config
        self.output_parser = output_parser
def parse_output2(res):
    res = Prompt2Model.model_validate_json(res.text)
    return res.suggestion
prompts = [
    Prompt(
        "Abdullah's Best Prompt",
        """\
You are a coding suggestion assistant. You will be given a uncompleted piece of code, alongwith the current position of the cursor in the text editor in which the code is being edited. 
Here is the code:
{code}
Your task is to give one to three lines of code starting from the line of the cursor. Only output suggested code in plain text. Don't write already given code.\
"""
	),
    Prompt(
        "Abdullah's Second Prompt",
	"""\
You are a smart coding assistant that gives coding suggestions. Given the context of the user's code editor, you have to suggest a few lines of code that should follow the user's cursor. Only output the code suggestion; don't include already given code.\
""",
		{
			"response_mime_type": "application/json",
			"response_json_schema": Prompt2Model.model_json_schema(),
			"thinking_config": types.ThinkingConfig(thinking_budget=-1)# dynamic thinking
		},
        parse_output2
	),
]