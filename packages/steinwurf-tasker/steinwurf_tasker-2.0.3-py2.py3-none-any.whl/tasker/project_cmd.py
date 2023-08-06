import sys
import invoke
from tasker.utils import validate
from steinnews import write_next_version, get_latest_tag, get_latest_changes
from steinnews.exceptions import NoChanges, InvalidChanges
from github import Github, GithubException
import os


def release(project, git, user, shell, registry, email, resolve_path, github_token):

    with shell.cd(project.path):

        current_branch = git.branch(shell)

        if current_branch != "master":
            if user.confirm(
                f'Your current branch is: "{current_branch}". '
                "Is it OK to switch to the master?",
                assume_yes=True,
            ):
                # If you just merged the PR for your feature branch (and removed
                # the branch), then the pull operation will offer to delete the
                # local branch
                git.checkout(shell, branch="master")
            else:
                return

        git.pull(shell)
        if not project.has_file("NEWS.rst"):

            raise invoke.exceptions.Exit(
                f"{project.file_path('NEWS.rst')} does not exists"
            )

        print("Automatically updating NEWS.rst.")
        latest_changes = []
        try:
            if github_token:
                with open(project.file_path("NEWS.rst")) as f:
                    latest_changes = get_latest_changes(f.read())
            new_tag = write_next_version(
                project.file_path("NEWS.rst"), project.file_path("NEWS.rst")
            )
        except NoChanges:
            if not user.confirm(
                "No changes found in the latest section. Is the news file updated?"
            ):
                raise invoke.exceptions.Exit(
                    "Aborting the release. Please update the latest section of the news file."
                )
            with open(project.file_path("NEWS.rst")) as f:
                new_tag = ".".join(get_latest_tag(f.read()))

        except InvalidChanges as e:
            raise invoke.exceptions.Exit(f"Invalid changes found: {e.invalid_changes}")

        print("Version updated to: ", new_tag)

        current_tags = git.tags(shell)
        current_tags.reverse()
        print("Current tags:\n{}".format(", ".join(current_tags)))

        # The VERSION variable is updated automatically in the wscript
        if project.has_file("wscript"):
            wscript_path = project.file_path("wscript")

            # All line endings should be translated to \n
            with open(wscript_path, "r") as wscript_content:
                lines = wscript_content.readlines()
            version_found = False
            for i, line in enumerate(lines):
                if line.startswith(("VERSION =", "VERSION=")):
                    lines[i] = f'VERSION = "{new_tag}"\n'
                    version_found = True
                    break
            if not version_found:
                if not user.confirm(
                    f'"VERSION =" string was not found in {wscript_path}." '
                    "Do you want to continue?"
                ):
                    raise invoke.exceptions.Exit("User Quit")
            else:
                # Make sure that our Unix-style line endings are preserved
                with open(wscript_path, "w", newline="\n") as output:
                    output.writelines(lines)
                print("The version number was updated in the wscript.")

            # Check if we should run the prepare_release step
            if project.file_contains("wscript", "def prepare_release("):
                shell.run(
                    command=f"{sys.executable} waf configure --resolve_path={resolve_path}"
                )
                shell.run(command=f"{sys.executable} waf prepare_release")

        shell.run(command="git diff")

        if not user.confirm("Accept the changes?"):

            print("Rolling back changes.")
            git.checkout(shell, branch=".")
            return

        # We only build project that can be built
        if project.has_file("waf") and user.confirm("Run clean compilation test?"):
            run_cmd = user.prompt(
                "Run command (to check if it compiles):",
                default=f"{sys.executable} waf distclean configure --resolve_path={resolve_path} build",
            )
            shell.run(command=run_cmd)

            # Some projects (like platform and cpuid) needs information about the
            # machine to run its unit tests properly.
            if user.confirm("Run unit tests?"):
                shell.run(command=f"{sys.executable} waf --run_tests")

        if not user.confirm(f'Create new tag "{new_tag}", and push to master?'):
            print("Rolling back changes.")
            git.checkout(shell, branch=".")
            return

        shell.run(command=f'git commit -am "Preparing to create tag {new_tag}"')
        shell.run(command=f'git tag -a {new_tag} -m "version {new_tag}"')
        shell.run(command="git push --tags origin master")

        # Update the tag information in the registry for this project
        print("Updating tags in the registry...\n")
        registry.add_tag(shell, user, project.name, new_tag)

        if user.confirm("Announce release with email?", assume_yes=False):
            try:
                print("Trying to send email..")
                email.send_release_email(project, new_tag)
                print("Email Succeeded!")
            except Exception as e:
                print(e)
                print("Email Failed!")

        if project.has_file("waf") and project.file_contains("wscript", "def upload("):
            # Retry if exception is raised, i.e., if you type the wrong user
            # or password for the upload
            if user.confirm("Run waf upload?"):
                while True:
                    ret = shell.run(command=f"{sys.executable} waf build upload")
                    if ret.exited == 0:
                        break
                    elif not user.confirm("Run waf upload failed, try again?"):
                        break

        if github_token is None:
            print(
                "github-token is not set in .steinwurf-tasker.yml. Please set it to a personal access token with repo, admin:org and workflows access."
            )
            print(f"Version {new_tag} of {project.name} has been released!")
            return

        g = Github(github_token)
        org = g.get_organization("steinwurf")
        repo = org.get_repo(project.name)
        try:
            if not repo.get_workflow("release.yml"):
                print(f"Version {new_tag} of {project.name} has been released!")
                return
        except GithubException:
            print(f"Version {new_tag} of {project.name} has been released!")
            return
        latest_changes_str = ""
        for i in range(1, len(latest_changes), 2):
            latest_changes_str += latest_changes[i]
        if len(current_tags) > 0:
            full_changelog = f"**Full Changelog**:https://github.com/steinwurf/{project.name}/compare/{current_tags[0]}...{new_tag}"
            latest_changes_str = full_changelog + "\n\nNews:\n" + latest_changes_str

        repo.create_git_release(
            tag=new_tag,
            name=new_tag,
            message=latest_changes_str,
            draft=False,
            prerelease=False,
        )
    print(f"Version {new_tag} of {project.name} has been released!")
