import tempfile
import os
import json

from . import validate

url = "https://raw.githubusercontent.com/steinwurf/tag-registry/master/tags.json"
tag_registry_repo = "git@github.com:steinwurf/tag-registry.git"


class Registry(object):
    def add_tag(self, shell, user, project_name, tag):
        with tempfile.TemporaryDirectory() as tmp:
            with shell.cd(tmp):
                shell.run(
                    command=f"git clone {tag_registry_repo} tag-registry", hide=True
                )
                with shell.cd("tag-registry"):
                    tags_json = os.path.join(shell.cwd, "tags.json")
                    with open(tags_json, "r") as jsonFile:
                        tags = json.load(jsonFile)

                    if project_name not in tags:
                        if user.confirm(
                            f"project {project_name} does not have previous "
                            "tags in registry, do you wish to continue?"
                        ):
                            tags[project_name] = []
                        else:
                            return False

                    try:
                        validate.new_tag(tags[project_name])(tag)
                    except Exception as e:
                        print(e)
                        return False

                    tags[project_name].append(tag)

                    with open(tags_json, "w") as jsonFile:
                        json.dump(tags, jsonFile, indent=4, sort_keys=True)
                    shell.run(command=f"git add {tags_json}", hide=True)
                    shell.run(
                        command=f'git commit -m "Added tag {tag} for {project_name}"',
                        hide=True,
                    )

                    shell.run(command=f"git push", hide=True)

        return True
