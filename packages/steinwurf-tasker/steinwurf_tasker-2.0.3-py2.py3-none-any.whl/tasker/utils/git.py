from . import validate
import semver


class Git(object):
    def checkout(self, shell, branch):
        shell.run(f"git checkout {branch}", hide=True)

    def pull(self, shell):
        result = shell.run(f"git pull", hide=True)
        return "Updating" in result.stdout

    def branch(self, shell):
        """Get the current branch."""
        branch = shell.run("git rev-parse --abbrev-ref HEAD", hide=True).stdout.strip()
        if branch == "HEAD":
            return None
        else:
            return branch

    def tags(self, shell):
        output = shell.run(f"git tag -l", hide=True).stdout
        if not output:
            return []

        all_tags = set(output.split("\n"))

        valid_tags = set(validate.extract_valid_tags(all_tags))
        invalid_tags = all_tags - valid_tags

        return sorted(invalid_tags) + sorted(valid_tags, key=semver.parse_version_info)
