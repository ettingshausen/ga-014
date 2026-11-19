"""GA014 indoor-unit temperature sensors."""
from datetime import timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature

DOMAIN = "ga014"
SCAN_INTERVAL = timedelta(seconds=30)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up one temperature sensor per indoor unit."""
    if discovery_info is None:
        return
    add_entities([IndoorUnitTemperature(hass, discovery_info)], True)


class IndoorUnitTemperature(SensorEntity):
    """Room temperature reported by an indoor unit."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_should_poll = True

    def __init__(self, hass, discovery_info):
        """Initialize the sensor."""
        self._hass = hass
        self._id = discovery_info["id"]
        self._name = discovery_info["name"]
        self._attr_name = f"{self._name}温度"
        self._attr_unique_id = f"ga014_{self._id}_temperature"
        self._attr_native_value = None

    @property
    def available(self):
        """Return True when the gateway is reachable."""
        gw = self._hass.data.get(DOMAIN)
        return bool(gw and gw.available and self._id in gw._status)

    def update(self):
        """Read the latest room temperature from the gateway cache."""
        gw = self._hass.data.get(DOMAIN)
        if not gw:
            return
        status = gw._status.get(self._id)
        if not status:
            return
        try:
            self._attr_native_value = round(float(status["room_temp"]), 1)
        except (KeyError, TypeError, ValueError):
            self._attr_native_value = None
