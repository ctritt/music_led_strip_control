from json import JSONDecodeError, dumps, loads

from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required
from flask_openapi import swag_from
from libs.webserver.executer import Executer
from libs.webserver.executer_base import validate_schema
from libs.webserver.messages import (
    ConfigFileImported,
    ConfigFileNotFound,
    DeviceNotFound,
    DuplicateItem,
    InvalidConfigFile,
    UnprocessableEntity,
    UnsupportedMediaType,
)
from libs.webserver.schemas.general_settings_api_schema import (
    APPLY_GROUP_CONTROLS_SCHEMA,
    GET_GROUP_CONTROLS_SCHEMA,
    ONE_GENERAL_SETTING_SCHEMA,
    SET_GENERAL_SETTINGS_SCHEMA,
)
from loguru import logger

general_settings_api = Blueprint("general_settings_api", __name__)


@general_settings_api.get("/api/settings/general")
@login_required
@swag_from("docs/general_settings_api/get_general_settings.yml")
def get_general_settings():
    data_in = request.args.to_dict()

    if set(data_in) == {"setting_key"}:  # Get one specific general setting.
        if not validate_schema(data_in, ONE_GENERAL_SETTING_SCHEMA):
            return UnprocessableEntity.as_response()

        data_out = Executer.instance.general_settings_executer.get_general_setting(data_in["setting_key"])

        return jsonify(data_out)

    if not set(data_in):  # Get all general settings.
        data_out = Executer.instance.general_settings_executer.get_general_settings()

        return jsonify(data_out)

    return UnprocessableEntity.as_response()


@general_settings_api.post("/api/settings/general")
@login_required
@swag_from("docs/general_settings_api/set_general_settings.yml")
def set_general_settings():
    data_in = request.get_json()

    if not validate_schema(data_in, SET_GENERAL_SETTINGS_SCHEMA):
        return UnprocessableEntity.as_response()

    data_out = Executer.instance.general_settings_executer.set_general_setting(data_in["settings"])

    return jsonify(data_out)


@general_settings_api.get("/api/settings/general/group")
@login_required
@swag_from("docs/general_settings_api/get_group_controls.yml")
def get_group_controls():
    """Return the current effect and brightness for a group."""
    data_in = request.args.to_dict()

    if set(data_in) != {"group"} or not validate_schema(data_in, GET_GROUP_CONTROLS_SCHEMA):
        return UnprocessableEntity.as_response()

    data_out = Executer.instance.general_settings_executer.get_group_controls(data_in["group"])

    if data_out is DeviceNotFound:
        return DeviceNotFound.as_response()

    return jsonify(data_out)


@general_settings_api.post("/api/settings/general/group")
@login_required
@swag_from("docs/general_settings_api/apply_group_controls.yml")
def apply_group_controls():
    """Set the effect and brightness for every device in a group."""
    data_in = request.get_json()

    if not validate_schema(data_in, APPLY_GROUP_CONTROLS_SCHEMA):
        return UnprocessableEntity.as_response()

    general_settings = Executer.instance.general_settings_executer
    devices = general_settings.set_group_brightness(data_in["group"], data_in["brightness"])

    if devices is DeviceNotFound:
        return DeviceNotFound.as_response()

    effect_executer = Executer.instance.effect_executer
    if data_in["group"] == general_settings.all_devices_id:
        effect_out = effect_executer.set_active_effect_for_all(data_in["effect"])
        applied_effect = effect_out["effect"]
        general_settings.refresh_device(general_settings.all_devices_id)
    else:
        effect_out = effect_executer.set_active_effect_for_multiple([{"device": device_id, "effect": data_in["effect"]} for device_id in devices])
        if effect_out is DeviceNotFound or effect_out is DuplicateItem:
            return effect_out.as_response()
        applied_effect = data_in["effect"]
        for device_id in devices:
            general_settings.refresh_device(device_id)

    return jsonify(
        {
            "group": data_in["group"],
            "effect": applied_effect,
            "brightness": data_in["brightness"],
        }
    )


@general_settings_api.delete("/api/settings/general")
@login_required
@swag_from("docs/general_settings_api/reset_general_settings.yml")
def reset_general_settings():
    data_out = Executer.instance.general_settings_executer.reset_settings()

    return jsonify(data_out)


@general_settings_api.get("/api/settings/configuration/file")
@login_required
@swag_from("docs/general_settings_api/export_config.yml")
def export_config():
    logger.debug(f"Send file: {Executer.instance.general_settings_executer.export_config_path}")
    return send_file(Executer.instance.general_settings_executer.export_config_path, as_attachment=True, max_age=-1, mimetype="application/json")


@general_settings_api.post("/api/settings/configuration/file")
@login_required
@swag_from("docs/general_settings_api/import_config.yml")
def import_config():
    logger.debug("Import Config Request received.")

    if "imported_config" not in request.files:
        logger.error("Could not find the file key.")
        return ConfigFileNotFound.as_response()

    imported_config = request.files["imported_config"]
    content = imported_config.read()
    if content:
        try:
            logger.debug(f"File Received: {dumps(loads(content), indent=4)}")
            if Executer.instance.general_settings_executer.import_config(loads(content)):
                return ConfigFileImported.as_response()
            return InvalidConfigFile.as_response()

        except (JSONDecodeError, UnicodeDecodeError):
            return UnsupportedMediaType.as_response()

    return ConfigFileNotFound.as_response()
