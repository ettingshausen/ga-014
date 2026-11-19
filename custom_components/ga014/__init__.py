#有建议可以ywyhass@126.com交流
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_HOST,ATTR_NAME,EVENT_HOMEASSISTANT_START,EVENT_HOMEASSISTANT_STOP)
from custom_components.ga014.ga014 import *
#from homeassistant.core import (ServiceRegistry)
from homeassistant.helpers.discovery import load_platform
from homeassistant.helpers import entity_registry as er

import logging
_LOGGER = logging.getLogger(__name__)

# 配置文件的样式
CONFIG_SCHEMA = vol.Schema(
    {
        "ga014": vol.Schema({vol.Required(CONF_HOST): cv.string})
    },extra=vol.ALLOW_EXTRA)
        
def setup(hass, config):
    conf = config['ga014']
    hass.data['ga014']=GA014(hass,conf.get(CONF_HOST))
    def start_zinguo_update_keep_alive(event):
        hass.data['ga014'].start_keep_alive()
    def stop_zinguo_update_keep_alive(event):
        hass.data['ga014'].stop_keep_alive()
    hass.bus.listen_once(EVENT_HOMEASSISTANT_START, start_zinguo_update_keep_alive)
    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, stop_zinguo_update_keep_alive)
    
    status=hass.data['ga014']._status
    registry=er.async_get(hass)
    for key in status.keys():
        # Prefer the name reported by the gateway. If getroomlist failed,
        # fall back to the name already stored on the climate entity.
        name=(status[key].get('name') or '').strip()
        if not name:
            entity_id=registry.async_get_entity_id('climate', 'ga014', str(key))
            entry=registry.async_get(entity_id) if entity_id else None
            if entry:
                name=((entry.name or entry.original_name or '')).strip()
        if not name:
            name='内机%s' % key
        discovery_info = {'id': key, 'name': name}
        load_platform(hass, 'climate', 'ga014', discovery_info, config)
        load_platform(hass, 'sensor', 'ga014', discovery_info, config)
    return True        