from __future__ import annotations

import logging
import requests
import json

from iplocationchanger.exception.whatismyip_service_exception import WhatIsMyIPServiceException

logger = logging.getLogger(__name__)

class WhatIsMyIPService:
  def __init__(
    self: WhatIsMyIPService,
    api_key: str,
  ) -> None:
    if len(api_key) <= 0:
      raise Exception('Invalid API Key')
    self.api_key = api_key

  def get_ip(self: WhatIsMyIPService) -> tuple[bool, str]:
    res_body = self.request('ip')
    try:
      ip = res_body['ip_address']
      logger.debug(f'IP: {ip}')
      return ip
    except KeyError as e:
      raise WhatIsMyIPServiceException('Could not get IP address') from e
    

  def get_location_from_ip(
    self: WhatIsMyIPService, 
    ip: str,
  ) -> tuple[bool, str]:
    res_body = self.request('ip-address-lookup', {'input': ip})
    try:
      location = res_body['ip_address_lookup'][0]['country']
      logger.debug(f'Location: {location}')
      return location
    except KeyError as e:
      raise WhatIsMyIPServiceException('n') from e

  def validate_connection(
    self: WhatIsMyIPService, 
    country_code: str
  ) -> None:
    ip = self.get_ip()
    location = self.get_location_from_ip(ip)
    if (location.lower().strip() == country_code.lower().strip()):
      return
    raise WhatIsMyIPServiceException(f'{country_code} not {location}')
  
  def request(
    self: WhatIsMyIPService, 
    path: str,
    other_params: dict[str, str] = {},
  ) -> dict:
    url = f'https://api.whatismyip.com/{path}.php'
    params = {
      'key': self.api_key,
      'output': 'json',
    }
    params.update(other_params)

    res = requests.get(url, params=params)
    if res.status_code < 200 or res.status_code > 299:
      logger.debug(f'Status code: {res.status_code}')
      logger.debug(f'Response: {res.content.decode("utf-8")}')
      raise WhatIsMyIPServiceException(f'Could not complete request "{path}".')
    
    res_body = res.content.decode('utf-8')
    logger.debug(f'Response raw: {res_body}')
    self.check_request_error(res_body)

    try:
      res_body_dict = json.loads(res_body)
      logger.debug(f'response dict: {res_body_dict}')
    except json.decoder.JSONDecodeError as e:
      raise WhatIsMyIPServiceException('Invalid JSON') from e

    logger.debug(f'Response parsed: {res_body}')
    return res_body_dict


  def check_request_error(
    self: WhatIsMyIPService,
    res_body: str,
  ) -> None:
    lower_stripped = res_body.lower().strip()
    msg = ''

    if lower_stripped == '0':
      msg = 'API key was not entered'
    if lower_stripped == '1':
      msg = 'API key is invalid'
    if lower_stripped == '2':
      msg = 'API key is inactive'
    if lower_stripped == '3':
      msg = 'Too many lookups'
    if lower_stripped == '4':
      msg = 'No input'
    if lower_stripped == '5':
      msg = 'Invalid input'
    if lower_stripped == '6':
      msg = 'Unknown error'

    if msg != '':
      raise WhatIsMyIPServiceException(msg)
