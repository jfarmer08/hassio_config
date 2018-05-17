"""
Support for interface with an Sharp TV.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/media_player.sharptv/
"""
import logging
import socket
import time

import voluptuous as vol

from homeassistant.components.media_player import (
    DOMAIN, SUPPORT_NEXT_TRACK, SUPPORT_PREVIOUS_TRACK,
    SUPPORT_TURN_OFF, SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_STEP,
    SUPPORT_PAUSE, SUPPORT_SELECT_SOURCE, MediaPlayerDevice)
from homeassistant.const import (
    CONF_HOST, CONF_NAME, STATE_OFF, STATE_ON, STATE_UNKNOWN)
from homeassistant.helpers import config_validation as cv

CONF_PORT = "port"
CONF_USER = "user"
CONF_PASSWORD = "password"

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['sharp_aquos_rc==0.2']

SUPPORT_SHARPTV = SUPPORT_VOLUME_STEP | \
    SUPPORT_VOLUME_MUTE | SUPPORT_PREVIOUS_TRACK | \
    SUPPORT_NEXT_TRACK | SUPPORT_TURN_OFF | SUPPORT_SELECT_SOURCE

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Sharp TV platform."""
    # Validate that all required config options are given
    #if not validate_config({DOMAIN: config}, {DOMAIN: [CONF_HOST]}, _LOGGER):
    #    return False

    # Default the entity_name to 'Sharp TV Remote'
    name = config.get(CONF_NAME, 'Sharp TV Remote')

    # Generate a config for the Sharp lib
    remote_config = {
        "name": "HomeAssistant",
        "description": config.get(CONF_NAME, ''),
        "id": "ha.component.sharp",
        "host": config.get(CONF_HOST),
        "port": config.get(CONF_PORT, 10002),
        "user": config.get(CONF_USER, ""),
        "password": config.get(CONF_PASSWORD, "")
    }

    add_devices([SharpTVDevice(name, remote_config)])


# pylint: disable=abstract-method
class SharpTVDevice(MediaPlayerDevice):
    """Representation of a Sharp TV."""

    # pylint: disable=too-many-public-methods
    def __init__(self, name, config):
        """Initialize the sharp device."""
        from sharp_aquos_rc import TV
        self._device = TV(config["host"], 
                          config["port"], 
                          str(config["user"]), 
                          str(config["password"]))

        self._name = name
        # Assume that the TV is not muted
        self._muted = False
        self._state = STATE_UNKNOWN
        self._current_source = None
        self._source_list = {'0': 'TV /Antenna',
                             '1': 'HDMI_IN_1',
                             '2': 'HDMI_IN_2',
                             '3': 'HDMI_IN_3',
                             '4': 'HDMI_IN_4',
                             '5': 'COMPONENT IN',
                             '6': 'VIDEO_IN_1',
                             '7': 'VIDEO_IN_2',
                             '8': 'PC_IN'};
        self.update()

    def update(self):
        """Retrieve the latest data."""
        for i in range(5):
            try:
                p = self._device.power()
            
                if (p == 1): 
                    self._state = STATE_ON

                    if (self._device.mute() == 1): self._muted = True 
                    else: self._muted = False

                    inp = self._device.input()
                    self._current_source = self._source_list.get(inp)

                    _LOGGER.debug('Found Current Source [%s] [%d]', self._current_source, inp)
            
                elif (p == 0): self._state = STATE_OFF
                else: _LOGGER.debug('Found Unknown State [%s]', p)

                break
            except (socket.timeout, TimeoutError, OSError) as e:
            #except TimeoutError as e:
                time.sleep(2)
                if (i >= 4):
                    _LOGGER.warning('Exception: Timeout.  Current state [%s] Error [%s]', self._state, repr(e)) 
                pass
            except BaseException as e:
                time.sleep(2)
                if (i >= 4):
                    _LOGGER.warning('Exception: Unknown.  Current state [%s] Error [%s]', self._state, repr(e)) 
                pass

        return True

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._muted

    @property
    def source(self):
        """Return the current input source."""
        return self._current_source

    @property
    def source_list(self):
        """List of available input sources."""
        return sorted(list(self._source_list.values()))

    @property
    def supported_media_commands(self):
        """Flag of media commands that are supported."""
        return SUPPORT_SHARPTV

    def volume_up(self):
        """Volume up the media player."""
        self._device.volume(self._device.volume() + 1)

    def volume_down(self):
        """Volume down media player."""
        self._device.volume(self._device.volume() - 1)

    def mute_volume(self, mute):
        """Send mute command."""
        self._device.mute(0)
        if (self._device.mute() == 1): self._muted = True 
        else: self._muted = False

    def media_next_track(self):
        """Send next track command."""
        self._device.channel_up()

    def media_previous_track(self):
        """Send the previous track command."""
        self._device.channel_down()

    def media_pause(self):
        """Send the previous track command."""
        self._device.sleep(1)

    def turn_on(self):
        """Turn the media player on."""
        self._device.power_on_command_settings(2)
        self._device.power(1) 
        self.update()

    def turn_off(self):
        """Turn off media player."""
        self._device.power_on_command_settings(2)
        self._device.power(0) 
        self.update()

    def select_source(self, source):
        """Select input source."""
        for k, v in self._source_list.items():
            if v == source:
                self._device.input(k)
                _LOGGER.info('Source Selection: New Source [%s] Input [%s]', v, k) 

        self.update()

