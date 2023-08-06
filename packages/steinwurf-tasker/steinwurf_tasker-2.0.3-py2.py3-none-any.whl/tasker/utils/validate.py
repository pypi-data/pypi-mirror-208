# encoding: utf-8

import shutil
import semver


def is_valid_tag(tag):
    """
    Return True if the tag is valid.

    :param tag: The tag to test.
    """
    try:
        semver.VersionInfo.parse(tag)
        return True
    except ValueError:
        return False


def extract_valid_tags(tags):
    """
    Return list of all valid tags in given list of tags.

    :param tags: List of tags, both valid and invalid.
    """
    return [tag for tag in tags if is_valid_tag(tag)]


def get_most_recent_tag(tags):
    """
    Return most recent tag in given list of tags.

    :param tags: List of tags.
    """
    tags = extract_valid_tags(tags)
    if not tags:
        return None
    newest_tag = tags[0]
    for tag in tags:
        if semver.VersionInfo.parse(tag).match(f">{newest_tag}"):
            newest_tag = tag
    return newest_tag


def new_tag(current_tags):
    """
    Create a new tag validator.

    This can be used when a new tag needs to be created.

    :param current_tags: A list of the current tags. This is used for
                         validation - a new tag must not already exist,
                         and must be newer than the current ones.
    """
    newest_tag = get_most_recent_tag(current_tags)

    def _validate_new_tag(tag):
        if not is_valid_tag(tag):
            raise Exception(
                f'"{tag}" invalid. see http://semver.org/ for more infomation.'
            )
        if tag in current_tags:
            raise Exception(f'"{tag}" already exists')
        if newest_tag and semver.compare(tag, newest_tag) == -1:
            raise Exception(
                f'"{tag}" is lower than "{newest_tag}", choose a higher one.'
            )
        return tag

    return _validate_new_tag


def executable(program):
    program = shutil.which(program)
    if program is None:
        raise Exception(f"{program} is not a valid executable.")
    return program
