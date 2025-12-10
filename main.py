import typer
import importlib
from filereader import FileReader
from chunkerizer import chunkerize_file
from google import genai
from dotenv import load_dotenv
import os
from codebleu import calc_codebleu
import logging
import time
from exp_reg import log_experiment_params
import inspect

got_warning = False
class WarningCatcher(logging.Handler):
    def emit(self, record):
        global got_warning
        if record.levelno == logging.WARNING:
            # print("Caught a warning:", record.getMessage())
            got_warning = True

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(WarningCatcher())

load_dotenv()

GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
LLM_RETRIES = 3

app = typer.Typer()

def get_score(expected, actual, language):
    global got_warning
    result = calc_codebleu([expected], [actual], lang=language, weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
    if got_warning:
        got_warning = False
        return -1
    else:
        return result["codebleu"]

def get_llm_output(promptobj, formatted_ptext, gemini_config=None):
    client = genai.Client()
    for i in range(LLM_RETRIES):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=formatted_ptext,
                config=gemini_config,  
            )
            ret_val = promptobj.output_parser(response.text)
            break
        except Exception as e:
            time.sleep(15)# because of rate limits
            if i+1 == LLM_RETRIES:
                return None
            print("retrying for LLM...")
            print("error is:", e)
    print(f"got from LLM:\"{ret_val}\"")
    time.sleep(15)# because of rate limits
    return ret_val

def get_score_list(prompt_list, chunktuple, language, logging_file):
    scores = []
    for promptobj in prompt_list:
        formatted_ptext = promptobj.ptext.format(code=chunktuple[0])
        output = get_llm_output(promptobj, formatted_ptext, gemini_config=promptobj.gemini_config)
        # output = "# hello, world"
        # output = chunktuple[1]
        # chunktuple[1] = "# bye, world"
#         output = """
# print("harry bhai is coding")
# print("is he really coding?")
# call_a_function()
# call_another_function()
# """
#         chunktuple[1] = output
        if output == None:
            return None
        s = get_score(actual=output, expected=chunktuple[1], language=language)
        print(f"got score:{s}")
        if s != -1:
            scores.append(s)
        else:
            return None
        logging_file.write(str({
            "prompt_id": promptobj.id,
            "expected": chunktuple[1],
            "actual": output,
            "score": s
        }) + "\n")
    return scores

EXT_MAP = {
    ".py": "python",
    ".c": "c"
}
def get_curr_file_language(filepath):
    _, ext = os.path.splitext(filepath)
    return EXT_MAP.get(ext)
def transform_prompts(prompts):
    pnew = []
    for p in prompts:
        pnew.append({
            "id": p.id,
            "ptext": p.ptext,
            "gemini_config": p.gemini_config,
            "output_parser": inspect.getsource(p.output_parser)
        })
def _run_experiment(exp_data, exp_name):
    file_reader = FileReader(repos=exp_data.repos)
    scores = [0 for _ in range(len(exp_data.prompts))]
    if not os.path.exists(os.path.join(os.getcwd(), "logs")):
        os.mkdir(os.path.join(os.getcwd(), "logs"))
    while True:
        if (repo_name := file_reader.pull_next_repo()) == None:
            break
        print(f"repo_name:{repo_name}")
        if not os.path.exists(os.path.join(os.getcwd(), "logs", repo_name)):
            os.mkdir(os.path.join(os.getcwd(), "logs", repo_name))
        while (file_data := file_reader.read_next_file()) != None:
            file_name = os.path.basename(file_data["filepath"])
            log_file_path = os.path.join(os.getcwd(), "logs", repo_name, file_name.split(".")[0] + ".txt")
            with open(log_file_path, "w") as lf:
                if (language := get_curr_file_language(file_data["filepath"])) is None:
                    continue
                print(f"filename:{file_data["filepath"]} ; file bytes:{len(file_data["file_content"])}")
                chunks = chunkerize_file(file_data["file_content"], 5)
                for chunktuple in chunks:
                    latest_scores = get_score_list(exp_data.prompts, chunktuple, language, lf)
                    if None == latest_scores:
                        continue
                    for i in range(len(scores)):
                        scores[i] += latest_scores[i]
    print("scores:", scores)
    prompts_d = transform_prompts(exp_data.prompts)
    log_experiment_params(exp_name, prompts_d, exp_data.repos, "expect_last_line", "basic experiment")

@app.command()
def run_experiment(exp_id: int, exp_name: str):
    import_path = f"experiments.{exp_id}"
    try:
        exp_data = importlib.import_module(import_path)
    except Exception:
        raise typer.BadParameter(param_hint=f"No data available for experiment titled \"{exp_id}\"")
    print(exp_data.repos)
    _run_experiment(exp_data, exp_name)

if __name__ == "__main__":
    app()
