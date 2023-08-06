from pathlib import Path

file_name = "VERSION"

root = Path(__file__).resolve().parent.parent.parent.parent

path_to_version = root.joinpath(file_name)


def extract_version():

    content_dict = {}
    content_list = Path(path_to_version).read_text().splitlines()

    for item in content_list:
        # NOTE: Ignore comments within the version files
        if item.startswith("#") or item.startswith("//"):
            continue

        # NOTE: Ignore all value components (ie. value contains `=`)
        key, *tail = item.split("=")

        content_dict[key] = "".join(tail)

    tag = content_dict.get("VERSION")

    if not tag:
        raise ValueError("project version not set - add `VERSION` variable")

    return tag
