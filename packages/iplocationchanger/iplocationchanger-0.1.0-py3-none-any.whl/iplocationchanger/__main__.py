import argparse
import logging
import json
import atexit

from iplocationchanger.model.openvpn_credentials import OpenVPNCredentials
from iplocationchanger.service.location_changer_service import LocationChangerService
from iplocationchanger.exception.location_changer_service_exception import LocationChangerServiceException

parser = argparse.ArgumentParser(
  prog = 'iplocationchanger',
  description = 'Reliable IP location changer using OpenVPN and WhatIsMyIP.',
)

parser.add_argument(
  '-w', '--api-key',
  required=True,
  type=str,
  help='WhatIsMyIP API Key',
)

parser.add_argument(
  '-u', '--user',
  type=str,
  help='OpenVPN User',
)

parser.add_argument(
  '-p', '--password',
  type=str,
  help='OpenVPN password',
)

parser.add_argument(
  '-l', '--country',
  required=True,
  type=str,
  help='Location to assume',
)

parser.add_argument(
  '-o', '--openvpn',
  required=True,
  type=str,
  default='openvpn',
  help='OpenVPN execution binary path',
)

parser.add_argument(
  '-c', '--config',
  required=True,
  type=str,
  help='Config to country JSON mapping file path',
)

parser.add_argument(
  '-x', '--log_level',
  type=str,
  choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
  help='Log level',
  default='INFO',
)

def main(args: argparse.Namespace):
  try:
    with open(args.config) as f_ptr:
      config_to_country_map = json.load(f_ptr)
    assert type(config_to_country_map) == dict
  except Exception as e:
    logging.exception(e)
    exit(1)
  
  ovnc_path = ''

  try:
    ovnc = OpenVPNCredentials(args.user, args.password)
    ovnc_path = ovnc.file_path()
  except AttributeError:
    pass
  
  lcs = LocationChangerService(
    args.api_key,
    config_to_country_map,
    args.openvpn,
    openvpn_credentials_path=ovnc_path,
  )
  atexit.register(lcs.disconnect_region)

  try:
    lcs.connect_region(args.country)
  except LocationChangerServiceException as e:
    logging.error(e)
    exit(1)
  # Keep running
  logging.info(f'connected to {args.country}')
  input('Press ENTER to disconnect\n')

if __name__ == '__main__':
  args = parser.parse_args()

  logging.basicConfig(
    format='%(asctime)s %(levelname)s %(module)s %(message)s',
    level=logging.getLevelName(args.log_level),
  )
  main(args)
