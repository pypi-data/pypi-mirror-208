from __future__ import annotations

import subprocess
import requests
import logging

logger = logging.getLogger(__name__)

class Utils:
  @classmethod
  def run_proc(cls: Utils, cmd: list[str], expect_error=False) -> tuple[bool, str, str]:
    try:
      logger.debug(f'CMD: {cmd}')
      proc = subprocess.run(
        cmd,
        capture_output = True,
        check = True,
      )
      success = proc.returncode == 0

      stdout = proc.stdout.decode('utf-8')
      stderr = proc.stderr.decode('utf-8')
      logger.debug(f'STDOUT: {stdout}')
      logger.debug(f'STDERR: {stderr}')

      return (
        success,
        stdout,
        stderr,
      )
    except Exception as e:
      logger.debug(e, exc_info=True)
      if expect_error:
        return (
          True,
          'execution failed',
          '',
        )
      raise e
