from __future__ import annotations
from tempfile import TemporaryDirectory

class OpenVPNCredentials:
  def __init__(
    self: OpenVPNCredentials,
    user: str,
    password: str,
  ) -> None:
    self.td = TemporaryDirectory()
    self._file_path = f'{self.td.name}/openvpn_credentials'
    with open(self._file_path, 'w') as f_ptr:
      f_ptr.write(f'{user}\n')
      f_ptr.write(f'{password}\n')

  def file_path(
    self: OpenVPNCredentials,
  ) -> str:
    return self._file_path

  def __del__(
    self: OpenVPNCredentials,
  ) -> None:
    self.td.cleanup()
