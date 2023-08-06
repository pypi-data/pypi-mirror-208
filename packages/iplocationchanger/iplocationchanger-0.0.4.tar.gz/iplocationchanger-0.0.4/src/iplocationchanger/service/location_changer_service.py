from __future__ import annotations

import logging
import time

from iplocationchanger.service.openvpn_service import OpenVPNService
from iplocationchanger.service.whatismyip_service import WhatIsMyIPService
from iplocationchanger.exception.location_changer_service_exception import LocationChangerServiceException
from iplocationchanger.exception.whatismyip_service_exception import WhatIsMyIPServiceException
from iplocationchanger.exception.openvpn_service_exception import OpenVPNServiceException

logger = logging.getLogger(__name__)

class LocationChangerService:
  def __init__(
    self: LocationChangerService,
    whatismyip_api_key: str,
    openvpn_config_to_country_map: dict,
    openvpn_executable_path: str,
    openvpn_credentials_path: str = '',
  ) -> None:
    """Initialize LocationChangerService.
    Sample usage: 
    try:
      lcs = LocationChangerService(
        'whatismyip_api_key',
        'openvpn_config_to_country_map',
        'openvpn_executable_path',
        'openvpn_credentials_path',
      )
    finally:
      # Disconnect VPN connection
      lcs.disconnect_region()
    """
    self.wms = WhatIsMyIPService(whatismyip_api_key)
    self.ovs = OpenVPNService(
      openvpn_config_to_country_map,
      openvpn_executable_path,
      credentials_path=openvpn_credentials_path,
    )

  def disconnect_region(
    self: LocationChangerService,
  ) -> None:
    logger.debug('disconnecting...')
    self.ovs.disconnect()

  def connect_region(
    self: LocationChangerService,
    country: str,
    OPENVPN_DELAY: int = 5,
  ) -> None:
    logger.debug(f'connecting to {country}...')
    try:
      self.ovs.connect(country)
    except OpenVPNServiceException as e:
      raise LocationChangerServiceException(f'Could not connect to {country}') from e
    # buy openvpn some time
    time.sleep(OPENVPN_DELAY)
    try:
      self.wms.validate_connection(country)
    except WhatIsMyIPServiceException as e:
      raise LocationChangerServiceException(f'Could not connect to {country}') from e
    logger.debug(f'connected to {country}')
