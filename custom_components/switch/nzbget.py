"""
*** CURRENTLY WORK IN PROGRESS ***
Support for setting the NZBGet NZB client in pause.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.nzbget/
"""
from datetime import timedelta
import logging

from aiohttp.hdrs import CONTENT_TYPE
import requests
import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_SSL, CONF_HOST, CONF_NAME, CONF_PORT, CONF_PASSWORD, CONF_USERNAME,
    CONTENT_TYPE_JSON, STATE_OFF, STATE_ON)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.util import Throttle

_LOGGING = logging.getLogger(__name__)

DEFAULT_NAME = 'NZBGet Switch'
DEFAULT_PORT = 6789

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=5)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_SSL, default=False): cv.boolean,
    vol.Optional(CONF_USERNAME): cv.string,
})


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the NZBGet switch."""
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    ssl = 's' if config.get(CONF_SSL) else ''
    name = config.get(CONF_NAME)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    url = "http{}://{}:{}/jsonrpc".format(ssl, host, port)

    try:
        nzbgetapi = NZBGetAPI(
            api_url=url, username=username, password=password)
        nzbgetapi.update()
    except (requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError) as conn_err:
        _LOGGER.error("Error setting up NZBGet API: %s", conn_err)
        return False

    add_devices([NZBGetSwitch(nzbgetapi, name)])

class NZBGetSwitch(ToggleEntity):
    """Representation of a NZBGet switch."""

    def __init__(self, api, name):
        """Initialize the NZBGet switch."""
        self._name = name
        self.api = api
        self._state = STATE_OFF

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state == STATE_ON

    def turn_on(self, **kwargs):
        """Turn the device on."""
        self.api.resumedownload()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self.api.pausedownload()

    def update(self):
        """Get the latest data from NZBGet and updates the state."""
        active = self.api.status.get("DownloadPaused")
        self._state = STATE_OFF if active else STATE_ON

class NZBGetAPI(object):
    """Simple JSON-RPC wrapper for NZBGet's API."""

    def __init__(self, api_url, username=None, password=None):
        """Initialize NZBGet API and set headers needed later."""
        self.api_url = api_url
        self.status = None
        self.resumedownload = None
        self.pausedownload = None
        self.headers = {CONTENT_TYPE: CONTENT_TYPE_JSON}

        if username is not None and password is not None:
            self.auth = (username, password)
        else:
            self.auth = None
        self.update()

    def post(self, method, params=None):
        """Send a POST request and return the response as a dict."""
        payload = {'method': method}

        if params:
            payload['params'] = params
        try:
            response = requests.post(
                self.api_url, json=payload, auth=self.auth,
                headers=self.headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as conn_exc:
            _LOGGER.error("Failed to update NZBGet status from %s. Error: %s",
                          self.api_url, conn_exc)
            raise

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Update cached response."""
        try:
            self.status = self.post('status')['result']
        except requests.exceptions.ConnectionError:
            # failed to update status - exception already logged in self.post
            raise
