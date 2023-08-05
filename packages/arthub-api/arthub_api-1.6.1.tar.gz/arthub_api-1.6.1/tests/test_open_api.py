import arthub_api
import pytest
import logging
from arthub_api import arthub_api_config
from . import _utils
from arthub_api import (
    OpenAPI,
    utils
)

TEST_DEPOT_NAME = "apg"

open_api = None


def on_api_failed(res):
    logging.error("[TEST][API] \"%s\" failed, error: %s" % (res.url, res.error_message()))


@pytest.mark.run(order=1)
def test_init(env):
    global open_api
    _c = _utils.get_config(env)
    open_api = OpenAPI(_c, False)
    res = open_api.login(arthub_api_config.account_email, arthub_api_config.password)
    if not res.is_succeeded():
        on_api_failed(res)
        pytest.exit("login failed, exit test", returncode=1)

    logging.info("[TEST][API] \"%s\" success, token: %s" % (res.url, res.results.get(0)["arthub_token"]))


def test_depot_get_root_id():
    res = open_api.depot_get_root_id(TEST_DEPOT_NAME)
    if not res.is_succeeded():
        on_api_failed(res)
        assert 0

    logging.info("[TEST][API] \"%s\" success, depot id: %d" % (res.url, res.results.get(0)))


def test_depot_get_node_brief_by_ids():
    res = open_api.depot_get_node_brief_by_ids(TEST_DEPOT_NAME, [120347220059298, 120347220059299])
    if not res.is_succeeded():
        on_api_failed(res)
        assert 0

    node_1 = res.results.get(0)
    node_2 = res.results.get(1)
    logging.info("[TEST][API] \"%s\" success, name_1: %s, name_2: %s" % (res.url, node_1["name"], node_2["name"]))


def test_depot_get_child_node_count():
    res = open_api.depot_get_child_node_count(TEST_DEPOT_NAME, [120347220059339])
    if not res.is_succeeded():
        on_api_failed(res)
        assert 0

    logging.info("[TEST][API] \"%s\" success, count: %d" % (res.url, res.results.get(0)["count"]))


def test_depot_get_download_signature():
    res = open_api.depot_get_download_signature(TEST_DEPOT_NAME,
                                                nodes=[{"object_id": 120347220059338, "object_meta": "origin_url"}])
    if not res.is_succeeded():
        on_api_failed(res)
        assert 0

    logging.info("[TEST][API] \"%s\" success, signed url: %s" % (res.url, res.results.get(0)["signed_url"]))


def test_depot_get_upload_signature():
    file_name = "new_asset_to_upload"
    res_0 = open_api.depot_create_asset(TEST_DEPOT_NAME, [{
        "parent_id": 120347220059339,
        "name": file_name,
        "add_new_version": False
    }])
    if not res_0.is_succeeded():
        on_api_failed(res_0)
        assert 0

    asset_id = res_0.results.get(0)["id"]

    res_1 = open_api.depot_get_upload_signature(TEST_DEPOT_NAME, nodes=[
        {"object_id": asset_id, "object_meta": "origin_url", "file_name": file_name}])
    if not res_1.is_succeeded():
        on_api_failed(res_1)
        assert 0

    logging.info("[TEST][API] \"%s\" success, signed url: %s" % (res_1.url, res_1.results.get(0)["signed_url"]))


def test_depot_get_child_node_id_in_range():
    res = open_api.depot_get_child_node_id_in_range(TEST_DEPOT_NAME, parent_id=120347220059339, offset=0, count=2,
                                                    query_filters=[{"meta": "type", "condition": "x != directory"}],
                                                    is_recursive=True)
    if not res.is_succeeded():
        on_api_failed(res)
        assert 0

    nodes = res.results.get(0)["nodes"]
    logging.info("[TEST][API] \"%s\" success" % res.url)


def test_depot_get_node_brief_by_path():
    res = open_api.depot_get_node_brief_by_path(TEST_DEPOT_NAME, root_id=120347220059296,
                                                path="open_api_test/asset.jpg")
    if not res.is_succeeded():
        on_api_failed(res)
        assert 0

    node = res.results.get(0)
    logging.info("[TEST][API] \"%s\" success, name: %s" % (res.url, node["name"]))


def test_depot_add_asset_tag():
    res = open_api.depot_add_asset_tag(TEST_DEPOT_NAME, asset_id=120347220059344, tag_name=[utils.get_random_string(5)])
    if not res.is_succeeded():
        on_api_failed(res)
        assert 0

    node = res.results.get(0)
    logging.info("[TEST][API] \"%s\" success, tag id: %d" % (res.url, node))


def test_get_account_detail():
    res = open_api.get_account_detail()
    if not res.is_succeeded():
        on_api_failed(res)
        assert 0

    logging.info("[TEST][API] \"%s\" success, email: %s" % (res.url, res.results.get(0)["email"]))


def test_get_ticket():
    res = open_api.get_ticket()
    if not res.is_succeeded():
        on_api_failed(res)
        assert 0

    logging.info("[TEST][API] \"%s\" success, ticket: %s" % (res.url, res.results.get(0)))


def test_get_last_access_location_by_account():
    res = open_api.get_last_access_location_by_account()
    if not res.is_succeeded():
        on_api_failed(res)
        assert 0

    logging.info("[TEST][API] \"%s\" success, last access location: %s" % (res.url, res.results.get(0)))


def test_depot_create_directory():
    res = open_api.depot_create_directory(TEST_DEPOT_NAME, [{
        "parent_id": 120347220059339,
        "name": "new_dir",
        "allowed_rename": True,
        "return_existing_id": False
    }])
    if not res.is_succeeded():
        on_api_failed(res)
        assert 0

    logging.info("[TEST][API] \"%s\" success, new dir id: %s" % (res.url, res.results.get(0)["id"]))


def test_depot_create_multi_asset():
    res = open_api.depot_create_multi_asset(TEST_DEPOT_NAME, [{
        "parent_id": 120347220059339,
        "name": "new_multi_asset"
    }])
    if not res.is_succeeded():
        on_api_failed(res)
        assert 0

    logging.info("[TEST][API] \"%s\" success, new multi asset id: %s" % (res.url, res.results.get(0)["id"]))


def test_depot_move_node():
    res = open_api.depot_move_node(TEST_DEPOT_NAME, ids=[120347220064827], other_parent_id=120347220064825)
    if not res.is_succeeded():
        on_api_failed(res)
        assert 0

    logging.info("[TEST][API] \"%s\" success" % res.url)
