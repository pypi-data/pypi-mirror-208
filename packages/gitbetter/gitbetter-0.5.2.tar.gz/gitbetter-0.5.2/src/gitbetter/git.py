import os

from pathier import Pathier


def execute(command: str) -> int:
    """Execute git command.

    Equivalent to `os.system(f"git {command}")`

    Returns the output of the `os.system` call."""
    return os.system(f"git {command}")


def new_repo():
    """>>> git init -b main"""
    execute("init -b main")


def loggy():
    """Equivalent to `git log --oneline --name-only --abbrev-commit --graph`."""
    execute("log --oneline --name-only --abbrev-commit --graph")


def status():
    """Execute `git status`."""
    execute("status")


# ======================================Staging/Committing======================================
def commit(args: str):
    """>>> git commit {args}"""
    execute(f"commit {args}")


def add(files: list[str] | None = None):
    """Stage a list of files.

    If no files are given (`files=None`), all files will be staged."""
    if not files:
        execute("add .")
    else:
        execute(f'add {" ".join(files)}')


def commit_files(files: list[str], message: str):
    """Stage and commit a list of files with commit message `message`."""
    add(files)
    commit(f'-m "{message}"')


def initcommit():
    """Equivalent to
    >>> git add .
    >>> git commit -m "Initial commit" """
    add()
    commit('-m "Initial commit"')


def amend(files: list[str] | None = None):
    """Stage and commit changes to the previous commit.

    If `files` is `None`, all files will be staged.

    Equivalent to:
    >>> git add {files}
    >>> git commit --amend --no-edit
    """
    add(files)
    commit("--amend --no-edit")


def tag(id_: str):
    """Tag the current commit with `id_`.

    Equivalent to `git tag {id_}`."""
    execute(f"tag {id_}")


# ==========================================Push/Pull==========================================
def add_remote_url(url: str, name: str = "origin"):
    """Add remote url to repo."""
    execute(f"remote add {name} {url}")


def push(args: str = ""):
    """Equivalent to `git push {args}`."""
    execute(f"push {args}")


def pull(args: str = ""):
    """Equivalent to `git pull {args}`."""
    execute(f"pull {args}")


def push_new_branch(branch: str):
    """Push a new branch to origin with tracking.

    Equivalent to `git push -u origin {branch}`."""
    push(f"-u origin {branch}")


def pull_branch(branch: str):
    """Pull `branch` from origin."""
    pull(f"origin {branch}")


# ============================================Checkout/Branches============================================
def branch(args: str):
    """Equivalent to `git branch {args}`."""
    execute(f"branch {args}")


def list_branches():
    """Print a list of branches."""
    branch("-vva")


def checkout(args: str):
    """Equivalent to `git checkout {args}`."""
    execute(f"checkout {args}")


def switch_branch(branch_name: str):
    """Switch to the branch specified by `branch_name`.

    Equivalent to `git checkout {branch_name}`."""
    checkout(branch_name)


def create_new_branch(branch_name: str):
    """Create and switch to a new branch named with `branch_name`.

    Equivalent to `git checkout -b {branch_name} --track`."""
    checkout(f"-b {branch_name} --track")


def delete_branch(branch_name: str, local_only: bool = True):
    """Delete `branch_name` from repo.

    #### :params:

    `local_only`: Only delete the local copy of `branch`, otherwise also delete the remote branch on origin and remote-tracking branch."""
    branch(f"--delete {branch_name}")
    if not local_only:
        push(f"origin --delete {branch_name}")


def undo():
    """Undo uncommitted changes.

    Equivalent to `git checkout .`."""
    checkout(".")


def merge(branch_name: str):
    """Merge branch `branch_name` with currently active branch."""
    execute(f"merge {branch_name}")


# ===============================Requires GitHub CLI to be installed and configured===============================


def create_remote(name: str, public: bool = False):
    """Uses GitHub CLI (must be installed and configured) to create a remote GitHub repo.

    #### :params:

    `name`: The name for the repo.

    `public`: Set to `True` to create the repo as public, otherwise it'll be created as private."""
    visibility = "--public" if public else "--private"
    os.system(f"gh repo create {name} {visibility}")


def create_remote_from_cwd(public: bool = False):
    """Use GitHub CLI (must be installed and configured) to create a remote GitHub repo from
    the current working directory repo and add its url as this repo's remote origin.

    #### :params:

    `public`: Create the GitHub repo as a public repo, default is to create it as private."""
    visibility = "public" if public else "private"
    os.system(f"gh repo create --source . --{visibility} --push")


def make_private(owner: str, name: str):
    """Uses GitHub CLI (must be installed and configured) to set the repo's visibility to private.

    #### :params:

    `owner`: The repo owner.

    `name`: The name of the repo to edit."""
    os.system(f"gh repo edit {owner}/{name} --visibility private")


def make_public(owner: str, name: str):
    """Uses GitHub CLI (must be installed and configured) to set the repo's visibility to public.

    #### :params:

    `owner`: The repo owner.

    `name`: The name of the repo to edit."""
    os.system(f"gh repo edit {owner}/{name} --visibility public")


def delete_remote(owner: str, name: str):
    """Uses GitHub CLI (must be isntalled and configured) to delete the remote for this repo.

    #### :params:

    `owner`: The repo owner.

    `name`: The name of the remote repo to delete."""
    os.system(f"gh repo delete {owner}/{name} --yes")
