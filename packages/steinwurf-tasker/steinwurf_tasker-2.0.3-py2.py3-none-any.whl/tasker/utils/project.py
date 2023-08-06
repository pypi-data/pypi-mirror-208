import os
import mmap
import invoke


class Project(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def has_file(self, file):
        file_path = self.file_path(file)
        return os.path.exists(file_path) and os.path.isfile(file_path)

    def file_contains(self, file, string):
        with open(self.file_path(file), "rb") as f, mmap.mmap(
            f.fileno(), 0, access=mmap.ACCESS_READ
        ) as s:
            return s.find(string.encode()) != -1

    def file_path(self, file):
        return os.path.abspath(os.path.expanduser(os.path.join(self.path, file)))


def find_project(c, name):

    project_paths = []
    if "project_path" in c.config:
        project_paths = [c.config.project_path]
    else:
        project_paths = c.config.project_paths
    assert type(project_paths) == list

    for project_path in project_paths:
        path = os.path.join(project_path, name)
        if os.path.exists(path):
            return Project(name, path)
    else:
        raise invoke.exceptions.Exit(f'The project "{name}" was not found.')
