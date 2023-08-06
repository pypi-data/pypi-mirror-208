# Copyright 2023 Agnostiq Inc.


from functools import partial
from pathlib import Path

import toml

from ..shared.classes.settings import Settings


class AuthConfigManager:
    @staticmethod
    def get_config_file(settings=Settings()):
        path = Path(settings.auth.config_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path.resolve())

    @staticmethod
    def get_auth_request_headers(settings=Settings()):
        return {"x-api-key": f"{AuthConfigManager.get_api_key(settings)}"}

    @staticmethod
    def save_token(token: str, settings=Settings()):
        auth_section_header = settings.auth.config_file_section
        token_keyname = settings.auth.cofig_file_token_keyname
        toml_dict = {}
        toml_dict[auth_section_header] = {}
        toml_dict[auth_section_header][token_keyname] = token or ""
        with open(AuthConfigManager.get_config_file(settings), "w") as f:
            toml.dump(toml_dict, f)

    @staticmethod
    def get_token(settings=Settings()):
        auth_section_header = settings.auth.config_file_section
        token_keyname = settings.auth.cofig_file_token_keyname
        token = settings.auth.token
        if not token:
            with open(AuthConfigManager.get_config_file(settings), "r") as f:
                toml_string = f.read()
                parsed_toml = toml.loads(toml_string)
                token = parsed_toml[auth_section_header][token_keyname]
        return token

    @staticmethod
    def get_api_key(settings=Settings()):
        auth_section_header = settings.auth.config_file_section
        api_keyname = settings.auth.config_file_api_key_keyname
        api_key = settings.auth.api_key
        if not api_key:
            with open(AuthConfigManager.get_config_file(settings), "r") as f:
                toml_string = f.read()
                parsed_toml = toml.loads(toml_string)
                api_key = parsed_toml[auth_section_header][api_keyname]
        return api_key

    @staticmethod
    def save_api_key(api_key: str, settings=Settings()):
        auth_section_header = settings.auth.config_file_section
        api_keyname = settings.auth.config_file_api_key_keyname
        toml_dict = {}
        toml_dict[auth_section_header] = {}
        toml_dict[auth_section_header][api_keyname] = api_key or ""
        with open(AuthConfigManager.get_config_file(settings), "w") as f:
            toml.dump(toml_dict, f)


get_token = partial(AuthConfigManager.get_token)
save_token = partial(AuthConfigManager.save_token)

get_api_key = partial(AuthConfigManager.get_api_key)
save_api_key = partial(AuthConfigManager.save_api_key)
