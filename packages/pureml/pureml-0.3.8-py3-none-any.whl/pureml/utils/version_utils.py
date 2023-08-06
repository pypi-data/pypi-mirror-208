def parse_version_label(label: str):
    name = None
    branch = None
    version = "latest"

    if label is None:
        return name, branch, version

    separator_count = label.count(":")

    if separator_count == 0:
        name = label
    elif separator_count == 1:
        name, branch = label.split(":")
    elif separator_count == 2:
        name, branch, version = label.split(":")

    return name, branch, version


def validate_name(name: str):
    pass


def validate_branch(branch: str):
    pass


def validate_version(version: str):
    pass


def generate_label(name: str, branch: str, version: str = "latest"):
    label = ":".join([name, branch, version])

    return label
