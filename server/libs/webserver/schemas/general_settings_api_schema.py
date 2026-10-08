from libs.webserver.schemas.config_validator_service import effect_enum, general_settings_schema, remove_required_keys
from libs.webserver.schemas.custom_types import valid_group_id_type

_GENERAL_SETTINGS_SCHEMA_PARSED = remove_required_keys(general_settings_schema)
""" Parsed general settings schema. Using schema from config validator service to avoid duplication. """

ONE_GENERAL_SETTING_SCHEMA = {
    "type": "object",
    "required": ["setting_key"],
    "properties": {
        "setting_key": {
            "type": "string",
            "enum": [
                "default_sample_rate",
                "device_groups",
                "device_id",
                "frames_per_buffer",
                "log_file_enabled",
                "log_level_console",
                "log_level_file",
                "max_frequency",
                "min_frequency",
                "min_volume_threshold",
                "n_fft_bins",
                "n_rolling_history",
                "webserver_port",
            ],
        },
    },
}
""" Schema for `GET /api/settings/general` with `setting_key` as a query parameter. """


_GENERAL_SETTINGS_PROPS = _GENERAL_SETTINGS_SCHEMA_PARSED["properties"]
SET_GENERAL_SETTINGS_SCHEMA = {
    "type": "object",
    "required": ["settings"],
    "properties": {
        "settings": {
            "type": "object",
            "properties": _GENERAL_SETTINGS_PROPS,
            "additionalProperties": False,
        },
    },
}
""" Schema for `POST /api/settings/general`. """


_ALL_EFFECTS = [*effect_enum, "effect_off", "effect_random_cycle", "effect_random_music", "effect_random_non_music"]

_GROUP_OR_ALL_TYPE = {
    "anyOf": [
        valid_group_id_type,
        {
            "type": "string",
            "enum": ["all_devices"],
        },
    ],
}
""" A group id or ``all_devices``. """


GET_GROUP_CONTROLS_SCHEMA = {
    "type": "object",
    "required": ["group"],
    "properties": {
        "group": _GROUP_OR_ALL_TYPE,
    },
}
""" Schema for `GET /api/settings/general/group`. """


APPLY_GROUP_CONTROLS_SCHEMA = {
    "type": "object",
    "required": ["group", "effect", "brightness"],
    "properties": {
        "group": _GROUP_OR_ALL_TYPE,
        "effect": {
            "type": "string",
            "enum": _ALL_EFFECTS,
        },
        "brightness": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
        },
    },
}
""" Schema for `POST /api/settings/general/group`. """
