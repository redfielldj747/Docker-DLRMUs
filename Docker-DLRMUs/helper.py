import re
import subprocess
import docker

#returns IHS dictionaries by device keyed to serial number
def run_query_container(target_list, client, volumes):

   index = len(target_list)
   IHS_list = []
   query_results = []
   device_dict = {}

   for target in target_list:
      IHS_dict = {}
      query_container = client.containers.run("dlrmus_query", detach=True, name="dlrmus_query" + str(index),
                                              devices=["/dev/" + target + ":/dev/ttyACM0"], volumes=volumes)
      for line in query_container.logs(stream=True):
         line_info = (line.strip().decode())
         IHS_list.append(line_info)
         if ":" in line_info:
            k = line_info.split(":")
            IHS_dict.update({k[0]:k[1]})
      ScannerSN = IHS_dict.get("SerialNumber")
      device_dict[ScannerSN] = IHS_dict

      index = index - 1

   return device_dict

#returns list of update container ids, starts scanner firmware update with containers per port
def run_update_containers(target_list, client, volumes):

   index = len(target_list) - 1
   update_containers = []

   while index > -1:
      stringdex = str(index)
      update_containers.append(client.containers.run("dlrmus_update",detach=True,name="dlrmus_update"+stringdex,devices=["/dev/"+target_list[index]+":/dev/ttyACM0"],volumes=volumes))
      index = index - 1

   return update_containers

#destroys containers by regex on string
def destroy_containers_by_name(client, name_pattern):

    for container in client.containers.list(all=True):
        if re.search(name_pattern, container.name):
            container.stop()
            container.remove(force=True)
    return 0

#find all devices connected on tttACM devices
def find_tty_acm_devices():

   tty_acm_devices = []

   result = subprocess.run(['ls', '/dev/'], capture_output=True, text=True, check=True)
   devices = result.stdout.splitlines()

   for dev in devices:
      if re.match(r'ttyACM[0-9]+', dev):
         tty_acm_devices.append(dev)
   if tty_acm_devices:
      return tty_acm_devices
   else:
      print("No ttyACM devices found.")
      exit(1)

#checks if containers passed in are still running if not then exits
def check_container_running(containers, client):

   index = len(containers)
   while index > 0:
      container_info = client.containers.get(containers[index-1].id)
      container_state = container_info.attrs['State']
      status_snapshot = container_state.get("Status")
      if status_snapshot != "running":
         index  = index -1

   return 0
