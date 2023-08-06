from __future__ import annotations
from tempfile import TemporaryDirectory

import logging
import os

from iplocationchanger.utils.utils import Utils
from iplocationchanger.exception.openvpn_service_exception import OpenVPNServiceException

logger = logging.getLogger(__name__)

ASSETS_DIR = os.getcwd() + '/assets'

class OpenVPNService:

  def __init__(
    self: OpenVPNService,
    config_to_country: dict,
    openvpn_executable_path: str,
    credentials_path: str='',
  ):
    self.config_to_country = config_to_country

    self.has_credentials = False
    if len(credentials_path) > 0:
      self.credentials_path = credentials_path
      self.has_credentials = True

    self.openvpn_executable_path = openvpn_executable_path
    self.daemon_name = 'openvpn_iplocationchanger'

  def disconnect(self: OpenVPNService) -> None:
    cmd = ['sudo', 'killall', 'openvpn']
    _, stdout, stderr = Utils.run_proc(cmd, expect_error=True)
    logger.debug(f'STDOUT: {stdout}')
    if stderr != '':
      logger.error(f'STDERR: {stderr}')

  def connect(self: OpenVPNService, country: str) -> None:
    try:
      config_path = self.config_to_country[country]
    except KeyError as e:
      logger.debug(e)
      raise OpenVPNServiceException(f'Could not find config for {country}')

    cmd = [
      'sudo', self.openvpn_executable_path,
      '--auth-retry', 'nointeract',
      '--config', config_path,
      '--script-security', '2',
      '--daemon', self.daemon_name,
    ]
    if self.has_credentials:
      cmd.extend(['--auth-user-pass', self.credentials_path])

    logger.debug(f'CMD: {" ".join(cmd)}')
    success, stdout, stderr =  Utils.run_proc(cmd)

    logger.debug(f'STDOUT: {stdout}')
    if not success:
      logger.error(f'STDERR: {stderr}')
      raise OpenVPNServiceException(f'Could not connect to {country}')
  