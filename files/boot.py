#!/usr/bin/python
import json
import os
import socket
import sys
import syslog
import traceback

sys.stderr = sys.stdout

PXE_NODES = "/var/www/provision/nodes/pxe_nodes.json"

print("Content-Type: text/plain")
print()

pxe_header = "#!ipxe"
if "gPXE" in os.environ["HTTP_USER_AGENT"]:
  pxe_header = "#!gpxe"

def pxe_abort():
  """Abort the PXE boot, continue with the next boot device in the BIOS boot order"""
  print(pxe_header)
  print("exit")
  sys.exit(0)

remote_addr = os.environ["REMOTE_ADDR"]
hostname = ""
try:
  # from the name, e.g. c1-3 take c1-3
  hostname = socket.gethostbyaddr(remote_addr)[0].split(".")[0]
except socket.herror as e:
  syslog.syslog(syslog.LOG_ERR, f"Could not translate IP '{remote_addr}' to hostname: {e}")
  pxe_abort()

try:
  os.remove("/var/www/provision/reinstall/" + hostname)
except FileNotFoundError:
  # File not found -> we don't want a reinstall
  syslog.syslog(syslog.LOG_INFO, f"Host '{hostname}' is not scheduled for reinstall, skipping")
  pxe_abort()
except OSError as e:
  syslog.syslog(syslog.LOG_INFO, str(e))
  pxe_abort()

nodesettings = {}
try:
  with open(PXE_NODES) as f:
    j = json.load(f)
  nodesettings = j[hostname]
except KeyError:
  syslog.syslog(syslog.LOG_ERR, f"Host '{hostname}' could not be found in {PXE_NODES}")
  pxe_abort()

try:
  serialport = 'ttyS0'
  if 'serialport' in nodesettings:
    serialport = nodesettings['serialport']

  url = nodesettings["kickstart_server_url"]
  profile = nodesettings["kickstart_profile"]
  args = nodesettings["kickstart_kernel_args"]
  print(pxe_header)
  print(
    f"kernel {url}/vmlinuz "
    f"inst.ks={url}/{profile} "
    f"console={serialport},115200 console=tty0 {args}"
  )
  print("initrd " + nodesettings["kickstart_server_url"] + "/initrd.img")
  print("boot")

except Exception:  # noqa: BLE001
  syslog.syslog(syslog.LOG_ERR, f"Generic error when trying to handle '{hostname}' ({remote_addr}): {traceback.format_exc()}")
  pxe_abort()
