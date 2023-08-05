import shutil
from pathlib import Path

import pytest

from mimeo import Mimeograph
from mimeo.config import MimeoConfig
from mimeo.context import MimeoContextManager


@pytest.fixture(autouse=True)
def _teardown():
    yield
    # Teardown
    shutil.rmtree("test_mimeograph-dir")


@pytest.mark.asyncio()
async def test_produce():
    config = {
        "output": {
            "direction": "file",
            "format": "xml",
            "indent": 4,
            "xml_declaration": True,
            "directory_path": "test_mimeograph-dir",
            "file_name": "output",
        },
        "_templates_": [
            {
                "count": 10,
                "model": {
                    "SomeEntity": {
                        "ChildNode1": 1,
                        "ChildNode2": "value-2",
                        "ChildNode3": True,
                    },
                },
            },
        ],
    }
    mimeo_config = MimeoConfig(config)
    with MimeoContextManager(mimeo_config):
        mimeo = Mimeograph(mimeo_config)

        assert not Path("test_mimeograph-dir").exists()
        await mimeo.process()
        assert Path("test_mimeograph-dir").exists()
        for i in range(1, 11):
            file_path = f"test_mimeograph-dir/output-{i}.xml"
            assert Path(file_path).exists()

            with Path(file_path).open() as file:
                assert file.readline() == '<?xml version="1.0" encoding="utf-8"?>\n'
                assert file.readline() == "<SomeEntity>\n"
                assert file.readline() == "    <ChildNode1>1</ChildNode1>\n"
                assert file.readline() == "    <ChildNode2>value-2</ChildNode2>\n"
                assert file.readline() == "    <ChildNode3>true</ChildNode3>\n"
                assert file.readline() == "</SomeEntity>\n"




