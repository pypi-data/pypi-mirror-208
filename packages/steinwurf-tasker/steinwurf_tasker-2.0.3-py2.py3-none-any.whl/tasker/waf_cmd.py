import sys
import shutil
import invoke


def deploy(project, git, shell, user, new_waf, resolve_path):
    assert project.has_file("waf")

    with shell.cd(project.path):

        current_branch = git.branch(shell)

        if current_branch != "master":
            if user.confirm(
                f'Your current waf branch is: "{current_branch}". '
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

        print("Copying new waf...")
        shutil.copyfile(new_waf, project.file_path("waf"))

        print(f"Configuring {project.name} with new waf...")
        shell.run(
            command=f"{sys.executable} waf distclean configure --resolve_path={resolve_path}",
            hide=True,
        )

        print(f"Building {project.name}...")
        shell.run(command=f"{sys.executable} waf build", hide=True)

        print(f"Update {project.name}'s NEWS.rst.")
        if project.has_file("NEWS.rst"):
            news_path = project.file_path("NEWS.rst")

            # All line endings should be translated to \n
            with open(news_path, "r") as input:
                lines = input.readlines()
            latest_heading_found = False
            for i, line in enumerate(lines):
                if i + 2 > len(lines):
                    break

                if line == "Latest\n" and lines[i + 1] == "------\n":
                    news_line = "* Minor: Updated waf.\n"
                    if lines[i + 2] == "* tbd\n":
                        lines[i + 2] = news_line
                    elif lines[i + 2] != news_line:
                        lines.insert(i + 2, news_line)
                    latest_heading_found = True
                    break

            if not latest_heading_found:
                print(f"Latest header was not found in {news_path}.")
                if user.confirm("Do you want to edit it manually?"):
                    user.open(shell, "NEWS.rst")
                elif not user.confirm("Do you want to continue?"):
                    raise invoke.exceptions.Exit("User Quit")
            else:
                # Make sure that our Unix-style line endings are preserved
                with open(news_path, "w", newline="\n") as output:
                    output.writelines(lines)
                print("The news file was automatically updated.")

        shell.run(command="git diff NEWS.rst")
        shell.run(command="git status")

        if not user.confirm("Accept the changes and commit directly on master?"):
            print("Rolling back changes.")
            git.checkout(shell, branch=".")
            return

        shell.run(command=f'git commit -am "Updated waf"')
        shell.run(command="git push")


def build(waf_project, shell, git, user, resolve_path):

    with shell.cd(waf_project.path):

        current_branch = git.branch(shell)

        if current_branch != "master":
            if user.confirm(
                f'Your current waf branch is: "{current_branch}". '
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
        print("Configuring waf project...")
        shell.run(
            command=f"{sys.executable} waf configure --resolve_path={resolve_path}",
            hide=True,
        )

        print("Building waf project...")
        shell.run(command=f"{sys.executable} waf build", hide=True)

        if not waf_project.has_file("build/waf"):
            raise invoke.exceptions.Exit(
                f"{waf_project.file_path('build/waf')} does not exists"
            )

        print("Build waf successfully!")
        return waf_project.file_path("build/waf")
