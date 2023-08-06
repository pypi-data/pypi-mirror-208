import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--env", action="store", default="oa",
        help="api config option: oa or qq or test_oa or test_qq"
    )


@pytest.fixture
def env(request):
    return request.config.getoption("--env")
