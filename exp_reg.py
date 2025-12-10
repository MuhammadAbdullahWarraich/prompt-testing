import mlflow
import os
import json
import shutil
from datetime import datetime

mlflow.set_tracking_uri("http://localhost:5000")

def log_experiment_params(experiment_name:str, prompt_set:list[dict],repos:list, chunk_policy:str, desc:str):
   
    mlflow.set_experiment(experiment_name)

    run_name = "Run_" + datetime.now().strftime("%Y%m%d_%H%M%S")

    with mlflow.start_run(run_name=run_name):
        mlflow.log_param("chunk_policy", chunk_policy)
        mlflow.log_param("description", desc)
        mlflow.log_param("repo_count", len(repos))


        os.makedirs("artifacts", exist_ok=True)

        prompt_set_path = "artifacts/prompt_set.json"
        with open(prompt_set_path, "w") as f:
            json.dump(prompt_set, f)
        mlflow.log_artifact(prompt_set_path)


        repos_path = "artifacts/repos.json"
        with open(repos_path, "w") as f:
            json.dump({"repos":repos}, f)
        mlflow.log_artifact(repos_path)

    print(f"Logged experiment '{experiment_name}' with parameters and artifacts.")            


# if __name__ == "__main__":

#     log_experiment_params(*["expeirment 1",
# {
#         "p1": "this is a good prompt",
#         "p2": "this is a bad prompt"
# }
# ,[
#         "https://github.com/muhammadabdullahwarraich/slowapi.git",
#         "https://github.com/muhammadabdullahwarraich/coroutines-library.git"
# ]
# , "chunk_at_end"
# ,"just a test experiment"])
