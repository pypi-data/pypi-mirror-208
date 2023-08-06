from aws_cdk import (
    assertions
)
import json


def print_template(template: assertions.Template):
    print(json.dumps(template.to_json(), indent=4))


def get_branch_name_from_mark(request):
    marker = request.node.get_closest_marker("branch_name")
    assert marker is not None
    branch_name = marker.args[0]
    return branch_name
