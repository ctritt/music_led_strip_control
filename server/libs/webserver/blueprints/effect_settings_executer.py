from __future__ import annotations

from libs.webserver.executer_base import ExecuterBase
from libs.webserver.messages import BadRequest, DeviceNotFound, NotFound, SettingNotFound


class EffectSettingsExecuter(ExecuterBase):
    def _devices_for_target(self, target: str) -> list[str] | DeviceNotFound:
        """Return device ids represented by a device, group, or ``all_devices``."""
        configs = self._config["device_configs"]

        if target == self.all_devices_id:
            device_ids = list(configs)
        elif target.startswith("group_") and target in self._config["general_settings"]["device_groups"]:
            device_ids = [device_id for device_id, config in configs.items() if target in config["device_groups"]]
        elif target in configs:
            device_ids = [target]
        else:
            return DeviceNotFound

        if not device_ids:
            return DeviceNotFound

        return device_ids

    def get_effect_setting(self, device: str, effect: str, setting_key: str) -> dict | DeviceNotFound | SettingNotFound:
        """Return the value of a setting for an effect.

        Groups and ``all_devices`` use the first device in that selection.
        """
        devices = self._devices_for_target(device)
        if devices is DeviceNotFound:
            return DeviceNotFound

        effect_settings = self._config["device_configs"][devices[0]]["effects"].get(effect)
        if effect_settings is None or setting_key not in effect_settings:
            return SettingNotFound

        return {"device": device, "effect": effect, "setting_key": setting_key, "setting_value": effect_settings[setting_key]}

    def get_effect_settings(self, device: str, effect: str) -> dict | DeviceNotFound | SettingNotFound:
        """Return all settings for an effect.

        Groups and ``all_devices`` use the first device in that selection.
        """
        devices = self._devices_for_target(device)
        if devices is DeviceNotFound:
            return DeviceNotFound

        effect_settings = self._config["device_configs"][devices[0]]["effects"].get(effect)
        if effect_settings is None:
            return SettingNotFound

        return {"device": device, "effect": effect, "settings": effect_settings}

    def set_effect_settings(self, device: str, effect: str, settings: dict) -> dict | NotFound | BadRequest:
        """Set effect settings for a device, a group, or all devices."""
        if not settings:
            return BadRequest  # Don't let an empty dict through.

        devices = self._devices_for_target(device)
        if devices is DeviceNotFound:
            return NotFound

        for device_id in devices:
            effect_settings = self._config["device_configs"][device_id]["effects"].get(effect)
            if effect_settings is None or any(setting_key not in effect_settings for setting_key in settings):
                return NotFound

        for device_id in devices:
            effect_settings = self._config["device_configs"][device_id]["effects"][effect]
            for setting_key, setting_value in settings.items():
                effect_settings[setting_key] = setting_value
            self.update_cycle_job(device_id, effect)

        self.save_config()
        if device == self.all_devices_id:
            self.refresh_device(self.all_devices_id)
        else:
            for device_id in devices:
                self.refresh_device(device_id)

        return {"device": device, "effect": effect, "settings": settings}

    def set_effect_settings_for_all(self, effect: str, settings: dict) -> dict | NotFound | BadRequest:
        """Set effect settings for all devices."""
        result = self.set_effect_settings(self.all_devices_id, effect, settings)
        if result is NotFound or result is BadRequest:
            return result

        return {"effect": effect, "settings": settings}

    def update_cycle_job(self, device: str, effect: str) -> None:
        """Change the Random Cycle Effect job interval on save."""
        if effect != "effect_random_cycle":
            return

        job = self.scheduler.get_job(device)
        if job:
            was_running = job.next_run_time
            interval = self._config["device_configs"][device]["effects"]["effect_random_cycle"]["interval"]
            self.scheduler.reschedule_job(device, trigger="interval", seconds=interval)
            if not was_running:  # Workaround flag because `reschedule_job()` unpauses jobs.
                self.scheduler.pause_job(device)
