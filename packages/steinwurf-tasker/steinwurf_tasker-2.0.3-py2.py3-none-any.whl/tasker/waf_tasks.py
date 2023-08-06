from fabric import task
from . import waf_cmd
from tasker.utils.project import find_project
from tasker.utils.git import Git
from tasker.utils.user import User


@task(
    help={
        "names": "The names of the projects to deploy to.",
    },
    iterable=["names"],
)
def deploy(c, names):
    """
    Builds a new waf from the latest waf master and then copies it to
    each of the give projects and creates a new branch on each of the projects.
    """
    user = User(c.config.editor)
    new_waf = None
    print(f"Updating waf in {len(names)} projects.")
    failed_projects = []
    for project_name in names:
        try:
            project = find_project(c, project_name)
            print(f"Deploying new waf to {project.name}.")
            if not project.has_file("waf"):
                print(f"{project.name} does not have a waf to replace.")
                continue
            if new_waf is None:
                new_waf = waf_cmd.build(
                    waf_project=find_project(c, "waf"),
                    shell=c,
                    git=Git(),
                    user=user,
                    resolve_path=c.config.resolve_path,
                )

            waf_cmd.deploy(
                project=project,
                new_waf=new_waf,
                shell=c,
                git=Git(),
                user=user,
                resolve_path=c.config.resolve_path,
            )
            print(f"Deploy successful.")
        except Exception as e:
            print(f"Deploy failed.")
            print(e)
            failed_projects.append(project_name)
            if not user.confirm("Continue?", assume_yes=True):
                break

    if failed_projects:
        print(f"The deployment failed in the following projects: {failed_projects}")
