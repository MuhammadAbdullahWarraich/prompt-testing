import os
import subprocess
from shutil import rmtree as shutil_rmtree
def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts
class FileReader:
    def __init__(self, repos):
        """
        repos: list of paths to local Git repositories
        """
        self.repos = repos
        self.currRepoFiles = []
        self.currFileIdx = 0

    def pull_next_repo(self):
        """
        Pulls the next repo in the list.
        If no repos left, returns None.
        Otherwise pulls, walks file structure, populates currRepoFiles, resets index, returns the repository's name.
        """
        if not self.repos:
            # if os.path.isdir('temp_repos'):
            #     shutil_rmtree('temp_repos')
            return None
        if not os.path.isdir('temp_repos'):
            os.mkdir('temp_repos')
        repo = self.repos.pop(0)
        repo_name = os.path.splitext(repo["link"].rstrip('/').split('/')[-1])[0]
        repo_path =  os.path.join(os.getcwd(), "temp_repos", repo_name)
        try:
            subprocess.run(
                ["git", "clone", repo["link"], repo_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to clone repo {repo_name}: {e.stderr.decode()}")

        # Walk repo and collect all file paths
        self.currRepoFiles = []
        for root, dirs, files in os.walk(repo_path):
            for f in files:
                full_path = os.path.join(root, f)
                if '.git' in splitall(full_path):
                    continue
                _, ext = os.path.splitext(full_path)
                if (include_exts := repo.get("include_exts")) is not None and ext not in include_exts:
                    continue
                self.currRepoFiles.append(full_path)

        self.currFileIdx = 0
        return repo_name

    def read_next_file(self):
        """
        Returns contents of the next file in current repo,
        or None if no more files.
        """
        if self.currFileIdx >= len(self.currRepoFiles):
            return None

        file_path = self.currRepoFiles[self.currFileIdx]
        self.currFileIdx += 1
        with open(file_path, "r") as f:
            file_content = f.readlines()
        print(f"...now reading file:{file_path}")
        return {
            "filepath": file_path,
            "file_content": file_content
        }
