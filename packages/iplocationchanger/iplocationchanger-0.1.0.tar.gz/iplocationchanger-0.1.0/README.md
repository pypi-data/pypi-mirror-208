# IP Location Changer

![tests](https://github.com/faaizz/iplocationchanger_python/actions/workflows/test.yaml/badge.svg)

Reliable IP location changer using [OpenVPN](https://openvpn.net/) and [WhatIsMyIP](https://www.whatismyip.com/).

This package allows changing the IP of the host machine by using openvpn configuration files (and optionally credentials), and verifying the IP location change using WhatIsMyIP.

## Usage
```python
from iplocationchanger.service.location_changer_service import LocationChangerService
from iplocationchanger.exception.location_changer_service_exception import LocationChangerServiceException


try:
  lcs = LocationChangerService(
    'reoiotiyotrkc77690543031b421b',
    {
      'TR': '/assets/NCVPN-TR-Istanbul-TCP.ovpn',
    },
    '/usr/local/openvpn',
    '/assets/openvpncredentials',
  )

  country = 'TR'
  try:
    lcs.connect_region(country)
    # Other code logic...

  except LocationChangerServiceException as e:
    # locaiton change failed
    logging.error(e)
    exit(1)
finally:
  lcs.disconnect_region()
```
### Standalone Execution
```shell
# Sample execution
python3 src/iplocationchanger/__main__.py \ 
  -w reoiotiyotrkc77690543031b421b \
  -l TR -o "/usr/local/openvpn" \
  -c "/assets/configmap.json" \
  -u "ncpuser@namecheap" -p "PaSsWoRd"
```


## Requirements
- Linux or macOS
- `openvpn` is installed on the host PC
- `openvpn` configuration files
- (optional) `openvpn` credentials
- WhatIsMyIP API Key
- User with `sudo` permissions without password requirements for `killall` and `openvpn`.

### Fulfilling `sudo` requirements without password prompt
Granting `sudo` requirements to a user without having them supply a password can be approached by editing the `/etc/sudoers` file as such:
```
username		ALL = (ALL) NOPASSWD: /usr/bin/killall, /usr/bin/openvpn
```

## Environment Setup
```shell
python3 -m venv ./.venv
source ./.venv/bin/activate

python -m pip install -r requirements/dev.txt
```

## Run tests
```shell
coverage run --rcfile .coveragerc  -m unittest discover -t src/ -s src/tests/unit

coverage report -m
```

## Config
Config files are JSON-formatted files with 2-letter [ISO 3166](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) country codes as `keys` and paths to corresponding OpenVPN configuration files as `values`.
A sample config file is shown below:
```json
{
  "TR": "/assets/NCVPN-TR-Istanbul-TCP.ovpn",
  "AR": "/assets/NCVPN-AR-Buenos-Aires-TCP.ovpn"
}
```
