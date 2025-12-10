import typer
import importlib
from filereader import FileReader

app = typer.Typer()

def _run_experiment(exp_data):
    file_reader = FileReader(repos=exp_data.repos)
    while True:
        if (repo_name := file_reader.pull_next_repo()) == None:
            break
        print(f"repo_name:{repo_name}")
        while (file_data := file_reader.read_next_file()) != None:
            assert str == type(file_data["file_content"])
            print(f"filename:{file_data["filepath"]} ; file bytes:{len(file_data["file_content"])}")
    print("ending")

@app.command()
def run_experiment(exp_id: int):
    import_path = f"experiments.{exp_id}"
    try:
        exp_data = importlib.import_module(import_path)
    except Exception:
        raise typer.BadParameter(param_hint=f"No data available for experiment titled \"{exp_id}\"")
    print(exp_data.repos)
    _run_experiment(exp_data)

if __name__ == "__main__":
    app()
