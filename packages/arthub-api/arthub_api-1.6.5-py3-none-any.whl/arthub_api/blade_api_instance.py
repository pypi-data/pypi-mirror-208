
# Import third-party modules
from .open_api import APIError
from . import BladeAPI, arthub_api_config
from .__main__ import init_config


blade_root_id = None
blade_backend = None


class BladeInstance(object):
    """Global instance initializer for BladeAPI client."""
    @classmethod
    def blade_root_id(cls):
        global blade_root_id
        if blade_root_id is None:
            res = cls.backend.blade_get_root_id()
            res.raise_for_err(res)
            root_id = res.result
            if root_id == 0:
                raise APIError("cannot get root id, result is 0")
            blade_root_id = root_id
        return blade_root_id

    @classmethod
    def backend(cls, recreate=False):
        global blade_backend
        if blade_backend is None or recreate:
            init_config()
            backend = BladeAPI(config=None)
            # this will login from file:  ~/Documents/ArtHub/arthub_api_config.py
            backend.init_from_config()
            if not arthub_api_config.blade_public_token and arthub_api_config.account_email:
                backend.login(arthub_api_config.account_email, arthub_api_config.password)
            blade_backend = backend
        return blade_backend
