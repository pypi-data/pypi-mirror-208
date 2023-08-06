import json
import os
import urllib.error
import urllib.parse
import urllib.request

import ruamel.yaml
from termcolor import colored

GITLAB_URL = "https://gitlab.com"
API_V4_URL = f"{GITLAB_URL}/api/v4"

HEADERS: dict[str, str] = {}
private_token = os.environ.get("GITLAB_PRIVATE_TOKEN")
if private_token:
    HEADERS.update({"PRIVATE-TOKEN": private_token})


def to_fragment(text):
    if not isinstance(text, str):
        return text
    return urllib.parse.quote(text, safe="")


def get_apiv4_url(url):
    try:
        url = f"{API_V4_URL}{url}"
        request = urllib.request.Request(url=url, headers=HEADERS)
        response = urllib.request.urlopen(request)
        content = response.read()
        return json.loads(content)
    except urllib.error.HTTPError:
        return None


def get_project(project_id):
    return get_apiv4_url(f"/projects/{to_fragment(project_id)}")


def get_latest_release(project_id):
    return get_apiv4_url(
        f"/projects/{to_fragment(project_id)}/releases/permalink/latest"
    )


def cproject(project_name):
    return colored(project_name, "magenta")


def ctag(tag_name):
    return colored(tag_name, "yellow", attrs=["bold"])


def update_include(include):
    if any(key not in include for key in ("project", "file")):
        return include

    project = get_project(include["project"])
    project_name = project["path_with_namespace"]

    latest_release = get_latest_release(project["id"])
    if latest_release:
        latest_tag = latest_release["tag_name"]
        current_tag = include.get("ref", None)
        if current_tag:
            if current_tag != latest_tag:
                print(
                    colored(project_name, "red", attrs=["bold"]),
                    "updated from {current} to {latest}".format(
                        current=ctag(current_tag),
                        latest=ctag(latest_tag),
                    ),
                )
            else:
                print(cproject(project_name), "is the latest at", ctag(current_tag))
        elif not current_tag:
            print(cproject(project_name), "pinned to", ctag(latest_tag))
        include["ref"] = latest_tag
    else:
        print(cproject(project_name), "has no releases")
    newinclude = {}
    newinclude["project"] = include["project"]
    if "ref" in include:
        newinclude["ref"] = include["ref"]
    newinclude["file"] = include["file"]
    return newinclude


def update_includes(includes):
    if not isinstance(includes, list):
        return includes

    return [update_include(include) for include in includes]


def update_command(args):
    yaml = ruamel.yaml.YAML()
    data = yaml.load(open(args.filename))

    if "include" in data:
        data["include"] = update_includes(data["include"])

    with open(args.filename, "w") as handle:
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.dump(data, handle)
