import subprocess

def subprocessRun(cmd_str: str, capture_output=True, shell=True, timeout=None) -> subprocess.CompletedProcess:
  """
  Wrapper for subprocess.run
  """
  return subprocess.run(cmd_str, capture_output=capture_output, shell=shell, timeout=timeout)