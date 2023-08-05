from mimeo import tools
from mimeo.resources.exc import ResourceNotFoundError
from tests.utils import assert_throws


def test_get_resource_existing():
    with tools.get_resource("logging.yaml") as resource:
        assert resource.name.endswith("resources/logging.yaml")


@assert_throws(err_type=ResourceNotFoundError,
               msg="No such resource: [{res}]",
               params={"res": "non-existing-file.yaml"})
def test_get_resource_non_existing():
    tools.get_resource("non-existing-file.yaml")
