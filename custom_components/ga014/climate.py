#有建议可以ywyhass@126.com交流
import json
import time
import voluptuous as vol

from homeassistant.components.climate import (ClimateDevice, PLATFORM_SCHEMA)
from homeassistant.components.climate.const import (
    ATTR_HVAC_MODE, HVAC_MODE_COOL, HVAC_MODE_DRY, HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT, SUPPORT_FAN_MODE, HVAC_MODE_AUTO, HVAC_MODE_OFF,
    SUPPORT_TARGET_TEMPERATURE,SUPPORT_SWING_MODE,SUPPORT_AUX_HEAT)
from homeassistant.const import (CONF_NAME, CONF_HOST, CONF_PORT,TEMP_CELSIUS, ATTR_TEMPERATURE,STATE_ON,STATE_OFF)
import homeassistant.helpers.config_validation as cv
import requests

import logging
_LOGGER = logging.getLogger(__name__)
from datetime import timedelta
SCAN_INTERVAL = timedelta(seconds=1)

#工作模式
MODE_HVAC={0:HVAC_MODE_OFF,1:HVAC_MODE_FAN_ONLY,2:HVAC_MODE_COOL,3:HVAC_MODE_HEAT,4:HVAC_MODE_AUTO,5:HVAC_MODE_DRY}
#风力模式
MODE_FAN ={0:'关',1:'一档风',2:'二档风', 3:'三档风', 4:'四档风', 5:'五档风', 6:'六档风', 7:'七档风',8:'自动风'}
#摇头模式
MODE_SWING={0:'关',1:'扫风'}

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    add_devices([Thermostat(hass,discovery_info)])


# pylint: disable=abstract-method
# pylint: disable=too-many-instance-attributes
class Thermostat(ClimateDevice):
    """Representation of a Midea thermostat."""

    def __init__(self,hass, conf):
        """Initialize the thermostat."""
        self._hass = hass
        self._name=conf.get('name');
        self._id=conf.get('id')
        self._room_temp=0
        self._set_temp=0
        self._run_mode=0
        self._fan_speed=0
        #电辅热
        self._aux=False
        #摇头模式
        self._swing=0
        self.time_start=0
        self.update()
        
    #支持的模式
    @property
    def supported_features(self):
        """Return the list of supported features."""
        return (SUPPORT_TARGET_TEMPERATURE|SUPPORT_FAN_MODE|SUPPORT_SWING_MODE|SUPPORT_AUX_HEAT)

    @property
    def should_poll(self):
        return True

    def update(self):
        if time.time()-self.time_start<10:
            return;
        status=self._hass.data['ga014']._status[self._id]
        #_LOGGER.debug(self._name)
        self._room_temp=float(status['room_temp'])
        self._set_temp=float(status['cool_temp_set'])
        self._run_mode=int(status['run_mode'])
        self._swing=int(status['is_swing'])
        self._aux=(int(status['is_elec_heat'])>0)
        if int(status['is_auto_fan'])!=0:
            self._fan_speed=8
        else:
            self._fan_speed=int(status['fan_speed'])

    @property
    def name(self):
        """Return the name of the thermostat."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    #当前室温
    @property
    def current_temperature(self):
        return self._room_temp

    #设置的温度
    @property
    def target_temperature(self):
        return self._set_temp

    def set_temperature(self, **kwargs):
        if self._run_mode>0:    
            self.time_start=time.time()
            self._set_temp=kwargs.get(ATTR_TEMPERATURE)
            self._hass.data['ga014'].set_status(self._id,self._run_mode,self._fan_speed,self._set_temp,self._aux,self._swing)

    #工作模式列表
    @property
    def hvac_modes(self):
        return list(MODE_HVAC.values())

    #工作模式
    @property
    def hvac_mode(self):
        return MODE_HVAC[self._run_mode]

    def set_hvac_mode(self, hvac):
        self._run_mode=list(MODE_HVAC.keys())[list(MODE_HVAC.values()).index(hvac)]
        self._hass.data['ga014'].set_status(self._id,self._run_mode,self._fan_speed,self._set_temp,self._aux,self._swing)
        
    #风力模式
    @property
    def fan_modes(self):
        """Return the list of available fan modes."""
        return list(MODE_FAN.values())
    
    @property
    def fan_mode(self):
        """Return the fan setting."""
        return MODE_FAN[self._fan_speed]

    def set_fan_mode(self, fan):
        if self._run_mode>0:
            self.time_start=time.time()
            self._fan_speed=list(MODE_FAN.keys())[list(MODE_FAN.values()).index(fan)]
            self._hass.data['ga014'].set_status(self._id,self._run_mode,self._fan_speed,self._set_temp,self._aux,self._swing)

    @property
    def is_aux_heat(self):
        return self._aux
        
    def turn_aux_heat_on(self):
        if self._run_mode>0:
            self.time_start=time.time()
            self._aux = True
            self._hass.data['ga014'].set_status(self._id,self._run_mode,self._fan_speed,self._set_temp,self._aux,self._swing)

    def turn_aux_heat_off(self):
        if self._run_mode>0:
            self.time_start=time.time()
            self._aux = False
            self._hass.data['ga014'].set_status(self._id,self._run_mode,self._fan_speed,self._set_temp,self._aux,self._swing)
        
    @property
    def swing_modes(self):
        return list(MODE_SWING.values())

    @property
    def swing_mode(self):
        return MODE_SWING[self._swing]

    def set_swing_mode(self, swing_mode):
        if self._run_mode>0:
            self.time_start=time.time()
            self._swing=list(MODE_SWING.keys())[list(MODE_SWING.values()).index(swing_mode)]
            self._hass.data['ga014'].set_status(self._id,self._run_mode,self._fan_speed,self._set_temp,self._aux,self._swing)
    