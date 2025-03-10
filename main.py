from helper import *
containers = []

#hardcoded query, but could be argurment or whatever later
query = "610099050"

client = docker.from_env()

destroy_containers_by_name(client, "dlrmus")

#this volume contains everything needed to run dlrmus and the 610099050 .S37 file, used for mounting
volumes = {
    'dlrmus': {'bind': '/dlrmus', 'mode': 'rw'}
}

#fill up list with target devices, will likely build switch between USB COM and OEM USB
target_list = find_tty_acm_devices()
print("Found scanners connected on these ports" + str(target_list))


containers = run_update_containers(target_list, client, volumes)
print("Started " + str(len(containers)) + " update containers, one per scanner")
print("Since update scanners are launched in detached mode, a function will now run to detect when they are finished running ")
containers_status = check_container_running(containers, client)

queried_values = run_query_container(target_list, client, volumes)
print("Starting query containers which will exit automatically after IHS info is gathered")

#could be set to ConfigurationFileID
query_field = "ApplicationROMID"

#only really works if scanners were on different firmware revision prior
for key in queried_values:
    value = (queried_values.get(key).get(query_field))
    if value == query:
        print("Scanner with serial number: " + key + " updated to 610099050, success!")
    else:
        print("Scanner with serial number: " + key + " did not update to 610099050, failure!")

destroy_containers_by_name(client, "dlrmus")


