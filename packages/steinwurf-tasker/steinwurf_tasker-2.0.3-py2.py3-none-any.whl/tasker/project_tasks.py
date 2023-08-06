from fabric import task
from . import project_cmd
from tasker.utils.git import Git
from tasker.utils.user import User
from tasker.utils.email import Email
from tasker.utils.registry import Registry
from tasker.utils.project import find_project


@task(help={"name": "Name of the project to release."})
def release(c, name):
    """
    Release a given project.
    """
    project_cmd.release(
        project=find_project(c, name),
        git=Git(),
        user=User(c.config.editor),
        shell=c,
        registry=Registry(),
        email=Email(**c.config.release_email),
        resolve_path=c.config.resolve_path,
        github_token=c.config.github_token,
    )
