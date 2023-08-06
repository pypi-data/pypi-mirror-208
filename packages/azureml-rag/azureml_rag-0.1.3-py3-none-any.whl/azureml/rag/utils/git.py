# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Functions for interacting with Git."""
import git
from pathlib import Path
from typing import Optional

from .azureml import get_secret_from_workspace
from .logging import get_logger


logger = get_logger('utils.git')
git_logger = get_logger('git_clone')


class GitCloneProgress(git.remote.RemoteProgress):
    """A progress handler for git clone operations"""
    def update(self, op_code, cur_count, max_count=None, message=''):
        """Update the progress of the git clone operation"""
        if message:
            git_logger.info(message.strip())

        if op_code & git.remote.RemoteProgress.BEGIN:
            git_logger.info("Begin clone")
        elif op_code & git.remote.RemoteProgress.END:
            git_logger.info("Clone complete")
        elif op_code & git.remote.RemoteProgress.COUNTING:
            git_logger.info("Received %d/%d objects" % (cur_count, max_count))


def get_keyvault_authentication(authentication_key_prefix: str):
    """Get the username and password for a keyvault authentication key"""""
    username = get_secret_from_workspace(f'{authentication_key_prefix}-USER')
    password = get_secret_from_workspace(f'{authentication_key_prefix}-PASS')
    return {'username': username, 'password': password}


def clone_repo(git_url: str, local_path: Path, branch: Optional[str] = None, authentication: Optional[dict] = None):
    """Clone a git repository to a local path, optionally checking out a branch"""
    logger.info(f'Cloning {git_url} to {local_path}')

    if authentication is not None:
        git_url = git_url.replace('https://', f'https://{authentication["username"]}:{authentication["password"]}@')

    logger.info(f'Cloning with depth={1 if branch is None else None}')
    repo = git.Repo.clone_from(git_url, local_path, progress=GitCloneProgress(), depth=1 if branch is None else None)
    if branch is not None:
        logger.info('fetch --all')
        repo.git.fetch("--all")
        logger.info(f'checkout {branch}')
        repo.git.checkout(branch)

    logger.info(f'Cloned branch "{repo.active_branch}" at commit: {repo.head.commit.hexsha}')
