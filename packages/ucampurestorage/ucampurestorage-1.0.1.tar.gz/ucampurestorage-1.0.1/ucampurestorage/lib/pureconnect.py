import re
from ucampurestorage.lib.httpclient import HttpClient
from ucampurestorage.lib.process import Process
import logging


LOG = logging.getLogger(__name__)


def totalbytes(value: str) -> int:
    valid_unit = ["k", "m", "g", "t", "p"]
    cap = int(value[:-1])
    unit = value[-1].lower()
    if unit not in valid_unit:
        raise "Invalid capacity unit"
    else:
        return converttobytes(cap, unit)


def converttobytes(value, fromtype, bsize=1024):
    """
    Converts megabytes to bytes, etc.
    sample code:
        print('mb= ' + str(bytesto(314575262000000, 'm')))
    sample output:
        mb= 300002347.946
    """
    unit = {"k": 1, "m": 2, "g": 3, "t": 4, "p": 5}
    result = float(value)
    for i in range(unit[fromtype]):
        result = result * bsize
    return result


class PureConnection:
    """
    Pure Storage API interface.

    Handles calls to Pure Storage Management via the REST API interface.
    """

    def __init__(
        self, host: any, port: int, user: str, password: any, token: any, verify: bool
    ):
        """
        This creates a connection to Dell Storage Manager.

        :param host: IP address of the Pure Storage.
        :param port: Port the Pure Storage is listening on.
        :param user: User account to login with.
        :param password: Password.
        :param token: valid token.
        :param verify: Boolean indicating whether certificate verification should be turned on or not.
        """
        self.notes = "Created via Pure Storage REST API"
        self.client = HttpClient(host, port, user, password, token, verify)
        self.controllers = None
        self.arrays = None
        self.volumes = None
        self.hosts = None
        self.volumegroups = None
        self.hostgroups = None
        self.volumesnapshots = None
        self.targetports = None
        self.networkports = None
        self.volumeconnections = None
        self.protectiongroups = None
        self.protectiongroupsnapshots = None
        self.protectiongroupvolmembers = None
        self.pods = None
        self.remotepods = None

    def _get_json(self, blob):
        """
        Returns a dict from the JSON of a REST response.

        :param blob: The response from a REST call.
        :returns: JSON or None on error.
        """
        try:
            return blob.json()
        except AttributeError:
            LOG.error("ERROR: invalid json")
        return None

    def _check_result(self, rest_response):
        """
        Checks and logs API responses.
        :param rest_response: The result from a REST API call.
        :returns: ``True`` if success, ``False`` otherwise.
        """
        if 200 <= rest_response.status_code < 300:
            return True
        return False

    def run_list_object(self, object_type):
        """
        Returns the result of get object functions and updates the corresponding data structures.

        :param object_type: the object type to list.
        :return: couple of (result of object get function, object data structure)
        """
        function_switcher = {
            "arrays": (self.get_arrays, "arrays"),
            "controllers": (self.get_controllers, "controllers"),
            "hosts": (self.get_hosts, "hosts"),
            "volumes": (self.get_volumes, "volumes"),
            "volumegroups": (self.get_volumegroups, "volumegroups"),
            "hostgroups": (self.get_hostgroups, "hostgroups"),
            "volumesnapshots": (self.get_volumesnapshots, "volumesnapshots"),
            "targetports": (self.get_targetports, "targetports"),
            "networkports": (self.get_networkports, "networkports"),
            "volumeconnections": (self.get_volumeconnections, "volumeconnections"),
            "protectiongroups": (self.get_protectiongroups, "protectiongroups"),
            "protectiongroupsnapshots": (
                self.get_protectiongroupsnapshots,
                "protectiongroupsnapshots",
            ),
            "protectiongroupvolmembers": (
                self.get_protectiongroupvolmembers,
                "protectiongroupvolmembers",
            ),
            "pods": (self.get_pods, "pods"),
            "remotepods": (self.get_remotepods, "remotepods"),
        }
        (get_object_func, data_structure) = function_switcher.get(object_type)
        result = get_object_func()
        return (result, getattr(self, data_structure)) if result else (result, None)

    def get_arrays(self):
        """
        Gets all arrays and updates `self.arrays`.
        :returns: `True` for success, `False` on error.
        """
        path = "/arrays"
        response = self.client.get(path)
        if not self._check_result(response):
            return False
        self.arrays = {}
        stdout = self._get_json(response)
        for i in range(len(stdout["items"])):
            self.arrays[stdout["items"][i]["name"]] = {}
            self.arrays[stdout["items"][i]["name"]]["id"] = stdout["items"][i]["id"]
            self.arrays[stdout["items"][i]["name"]]["os"] = stdout["items"][i]["os"]
            self.arrays[stdout["items"][i]["name"]]["version"] = stdout["items"][i][
                "version"
            ]
            self.arrays[stdout["items"][i]["name"]]["console_lock_enabled"] = stdout[
                "items"
            ][i]["console_lock_enabled"]
            self.arrays[stdout["items"][i]["name"]]["scsi_timeout"] = stdout["items"][
                i
            ]["scsi_timeout"]
            self.arrays[stdout["items"][i]["name"]]["capacity"] = stdout["items"][i][
                "capacity"
            ]
            self.arrays[stdout["items"][i]["name"]]["space"] = stdout["items"][i][
                "space"
            ]
            self.arrays[stdout["items"][i]["name"]]["encryption"] = stdout["items"][i][
                "encryption"
            ]
            self.arrays[stdout["items"][i]["name"]]["eradication_config"] = stdout[
                "items"
            ][i]["eradication_config"]
            self.arrays[stdout["items"][i]["name"]]["ntp_servers"] = stdout["items"][i][
                "ntp_servers"
            ]
        return True

    def get_controllers(self):
        """
        Gets all controllers and updates `self.controllers`.
        :returns: `True` for success, `False` on error.
        """
        path = "/controllers"
        response = self.client.get(path)
        if not self._check_result(response):
            return False
        self.controllers = {}
        stdout = self._get_json(response)

        for i in range(len(stdout["items"])):
            self.controllers[stdout["items"][i]["name"]] = {}
            self.controllers[stdout["items"][i]["name"]]["status"] = stdout["items"][i][
                "status"
            ]
            self.controllers[stdout["items"][i]["name"]]["model"] = stdout["items"][i][
                "model"
            ]
            self.controllers[stdout["items"][i]["name"]]["mode"] = stdout["items"][i][
                "mode"
            ]
            self.controllers[stdout["items"][i]["name"]]["version"] = stdout["items"][
                i
            ]["version"]
        return True

    def get_volumes(self, name=None):
        """
        Gets all volumes and updates `self.volumes`.
        :returns: `True` for success, `False` on error.
        """
        path = "/volumes"
        if name:
            path = f"/volumes?names={name}"
        response = self.client.get(path)
        if not self._check_result(response):
            return False
        self.volumes = {}
        stdout = self._get_json(response)
        for i in range(len(stdout["items"])):
            self.volumes[stdout["items"][i]["name"]] = {}
            self.volumes[stdout["items"][i]["name"]]["name"] = stdout["items"][i][
                "name"
            ]
            self.volumes[stdout["items"][i]["name"]]["created"] = stdout["items"][i][
                "created"
            ]
            self.volumes[stdout["items"][i]["name"]]["provisioned"] = stdout["items"][
                i
            ]["provisioned"]
            self.volumes[stdout["items"][i]["name"]]["id"] = stdout["items"][i]["id"]
            self.volumes[stdout["items"][i]["name"]]["serial"] = stdout["items"][i][
                "serial"
            ]
            self.volumes[stdout["items"][i]["name"]]["subtype"] = stdout["items"][i][
                "subtype"
            ]
            self.volumes[stdout["items"][i]["name"]]["destroyed"] = stdout["items"][i][
                "destroyed"
            ]
            self.volumes[stdout["items"][i]["name"]]["connection_count"] = stdout[
                "items"
            ][i]["connection_count"]
            self.volumes[stdout["items"][i]["name"]]["source"] = stdout["items"][i][
                "source"
            ]
            self.volumes[stdout["items"][i]["name"]]["space"] = stdout["items"][i][
                "space"
            ]
            self.volumes[stdout["items"][i]["name"]][
                "host_encryption_key_status"
            ] = stdout["items"][i]["host_encryption_key_status"]
            self.volumes[stdout["items"][i]["name"]]["pod"] = stdout["items"][i]["pod"]
            self.volumes[stdout["items"][i]["name"]]["volume_group"] = stdout["items"][
                i
            ]["volume_group"]
            self.volumes[stdout["items"][i]["name"]][
                "requested_promotion_state"
            ] = stdout["items"][i]["requested_promotion_state"]
            self.volumes[stdout["items"][i]["name"]]["promotion_status"] = stdout[
                "items"
            ][i]["promotion_status"]
            self.volumes[stdout["items"][i]["name"]]["priority_adjustment"] = stdout[
                "items"
            ][i]["priority_adjustment"]
        return True

    def get_hosts(self, name=None):
        """
        Gets all hosts and updates `self.hosts`.
        :returns: `True` for success, `False` on error.
        """
        path = "/hosts"
        if name:
            path = f"/hosts?names={name}"
        response = self.client.get(path)
        if not self._check_result(response):
            return False
        self.hosts = {}
        stdout = self._get_json(response)
        for i in range(len(stdout["items"])):
            self.hosts[stdout["items"][i]["name"]] = {}
            self.hosts[stdout["items"][i]["name"]]["is_local"] = stdout["items"][i][
                "is_local"
            ]
            self.hosts[stdout["items"][i]["name"]]["personality"] = stdout["items"][i][
                "personality"
            ]
            self.hosts[stdout["items"][i]["name"]]["host_group"] = stdout["items"][i][
                "host_group"
            ]
            self.hosts[stdout["items"][i]["name"]]["vlan"] = stdout["items"][i]["vlan"]
            self.hosts[stdout["items"][i]["name"]]["preferred_arrays"] = stdout[
                "items"
            ][i]["preferred_arrays"]
            self.hosts[stdout["items"][i]["name"]]["wwns"] = stdout["items"][i]["wwns"]
            self.hosts[stdout["items"][i]["name"]]["connection_count"] = stdout[
                "items"
            ][i]["connection_count"]
            self.hosts[stdout["items"][i]["name"]]["iqns"] = stdout["items"][i]["iqns"]
            self.hosts[stdout["items"][i]["name"]]["nqns"] = stdout["items"][i]["nqns"]
            self.hosts[stdout["items"][i]["name"]]["chap"] = stdout["items"][i]["chap"]
            self.hosts[stdout["items"][i]["name"]]["port_connectivity"] = stdout[
                "items"
            ][i]["port_connectivity"]
        return True

    def get_volumegroups(self):
        """
        Gets all volume-groups and updates `self.volumegroups`.
        :returns: `True` for success, `False` on error.
        """
        path = "/volume-groups"
        response = self.client.get(path)
        if not self._check_result(response):
            return False
        self.volumegroups = {}
        stdout = self._get_json(response)
        for i in range(len(stdout["items"])):
            self.volumegroups[stdout["items"][i]["name"]] = {}
            self.volumegroups[stdout["items"][i]["name"]]["id"] = stdout["items"][i][
                "id"
            ]
            self.volumegroups[stdout["items"][i]["name"]]["destroyed"] = stdout[
                "items"
            ][i]["destroyed"]
            self.volumegroups[stdout["items"][i]["name"]]["time_remaining"] = stdout[
                "items"
            ][i]["time_remaining"]
            self.volumegroups[stdout["items"][i]["name"]]["volume_count"] = stdout[
                "items"
            ][i]["volume_count"]
            self.volumegroups[stdout["items"][i]["name"]]["space"] = stdout["items"][i][
                "space"
            ]
            self.volumegroups[stdout["items"][i]["name"]]["qos"] = stdout["items"][i][
                "qos"
            ]
            self.volumegroups[stdout["items"][i]["name"]][
                "priority_adjustment"
            ] = stdout["items"][i]["priority_adjustment"]
        return True

    def get_hostgroups(self):
        """
        Gets all host-groups and updates `self.hostgroups`.
        :returns: `True` for success, `False` on error.
        """
        path = "/host-groups"
        response = self.client.get(path)
        if not self._check_result(response):
            return False
        self.hostgroups = {}
        stdout = self._get_json(response)
        for i in range(len(stdout["items"])):
            self.hostgroups[stdout["items"][i]["name"]] = {}
            self.hostgroups[stdout["items"][i]["name"]]["is_local"] = stdout["items"][
                i
            ]["is_local"]
            self.hostgroups[stdout["items"][i]["name"]]["host_count"] = stdout["items"][
                i
            ]["host_count"]
            self.hostgroups[stdout["items"][i]["name"]]["connection_count"] = stdout[
                "items"
            ][i]["connection_count"]
            self.hostgroups[stdout["items"][i]["name"]]["space"] = stdout["items"][i][
                "space"
            ]
        return True

    def get_volumesnapshots(self, name=None):
        """
        Gets all volume-snapshots and updates `self.volumesnapshots`.
        :returns: `True` for success, `False` on error.
        """
        path = "/volume-snapshots"
        if name:
            path = f"/volume-snapshots?source_names={name}"
        response = self.client.get(path)
        if not self._check_result(response):
            return False
        self.volumesnapshots = {}
        stdout = self._get_json(response)
        for i in range(len(stdout["items"])):
            self.volumesnapshots[stdout["items"][i]["name"]] = {}
            self.volumesnapshots[stdout["items"][i]["name"]]["id"] = stdout["items"][i][
                "id"
            ]
            self.volumesnapshots[stdout["items"][i]["name"]]["serial"] = stdout[
                "items"
            ][i]["serial"]
            self.volumesnapshots[stdout["items"][i]["name"]]["created"] = stdout[
                "items"
            ][i]["created"]
            self.volumesnapshots[stdout["items"][i]["name"]]["time_remaining"] = stdout[
                "items"
            ][i]["time_remaining"]
            self.volumesnapshots[stdout["items"][i]["name"]]["provisioned"] = stdout[
                "items"
            ][i]["provisioned"]
            self.volumesnapshots[stdout["items"][i]["name"]]["destroyed"] = stdout[
                "items"
            ][i]["destroyed"]
            self.volumesnapshots[stdout["items"][i]["name"]]["source"] = stdout[
                "items"
            ][i]["source"]
            self.volumesnapshots[stdout["items"][i]["name"]]["pod"] = stdout["items"][
                i
            ]["pod"]
            self.volumesnapshots[stdout["items"][i]["name"]]["space"] = stdout["items"][
                i
            ]["space"]
            self.volumesnapshots[stdout["items"][i]["name"]]["volume_group"] = stdout[
                "items"
            ][i]["volume_group"]
        return True

    def get_targetports(self):
        """
        Gets all ports and updates `self.target-ports`.
        :returns: `True` for success, `False` on error.
        """
        path = "/ports"
        response = self.client.get(path)
        if not self._check_result(response):
            return False
        self.targetports = {}
        stdout = self._get_json(response)
        for i in range(len(stdout["items"])):
            self.targetports[stdout["items"][i]["name"]] = {}
            self.targetports[stdout["items"][i]["name"]]["nqn"] = stdout["items"][i][
                "nqn"
            ]
            self.targetports[stdout["items"][i]["name"]]["iqn"] = stdout["items"][i][
                "iqn"
            ]
            self.targetports[stdout["items"][i]["name"]]["wwn"] = stdout["items"][i][
                "wwn"
            ]
            self.targetports[stdout["items"][i]["name"]]["portal"] = stdout["items"][i][
                "portal"
            ]
            self.targetports[stdout["items"][i]["name"]]["failover"] = stdout["items"][
                i
            ]["failover"]
        return True

    def get_networkports(self):
        """
        Gets all networkports and updates `self.target-ports`.
        :returns: `True` for success, `False` on error.
        """
        path = "/network-interfaces"
        response = self.client.get(path)
        if not self._check_result(response):
            return False
        self.networkports = {}
        stdout = self._get_json(response)
        for i in range(len(stdout["items"])):
            self.networkports[stdout["items"][i]["name"]] = {}
            self.networkports[stdout["items"][i]["name"]]["enabled"] = stdout["items"][
                i
            ]["enabled"]
            self.networkports[stdout["items"][i]["name"]]["speed"] = stdout["items"][i][
                "speed"
            ]
            self.networkports[stdout["items"][i]["name"]]["interface_type"] = stdout[
                "items"
            ][i]["interface_type"]
            self.networkports[stdout["items"][i]["name"]]["fc"] = stdout["items"][i][
                "fc"
            ]
            self.networkports[stdout["items"][i]["name"]]["eth"] = stdout["items"][i][
                "eth"
            ]
            self.networkports[stdout["items"][i]["name"]]["services"] = stdout["items"][
                i
            ]["services"]
        return True

    def get_volumeconnections(self, name=None):
        """
        Gets all connections and updates `self.volumeconnections`.
        :returns: `True` for success, `False` on error.
        """
        path = "/connections"
        if name:
            path = f"/connections?volume_names={name}"
        response = self.client.get(path)
        if not self._check_result(response):
            return False
        self.volumeconnections = {}
        stdout = self._get_json(response)
        for i in range(len(stdout["items"])):
            host_id = (
                stdout["items"][i]["host"]["name"]
                + "_ID:"
                + str(stdout["items"][i]["lun"])
            )
            self.volumeconnections[host_id] = {}
            self.volumeconnections[host_id]["host"] = stdout["items"][i]["host"]
            self.volumeconnections[host_id]["lun"] = stdout["items"][i]["lun"]
            self.volumeconnections[host_id]["volume"] = stdout["items"][i]["volume"]
            self.volumeconnections[host_id]["host_group"] = stdout["items"][i][
                "host_group"
            ]
            self.volumeconnections[host_id]["protocol_endpoint"] = stdout["items"][i][
                "protocol_endpoint"
            ]
        return True

    def get_protectiongroups(self):
        """
        Gets all networkports and updates `self.target-ports`.
        :returns: `True` for success, `False` on error.
        """
        path = "/protection-groups"
        response = self.client.get(path)
        if not self._check_result(response):
            return False
        self.protectiongroups = {}
        stdout = self._get_json(response)
        for i in range(len(stdout["items"])):
            self.protectiongroups[stdout["items"][i]["name"]] = {}
            self.protectiongroups[stdout["items"][i]["name"]]["is_local"] = stdout[
                "items"
            ][i]["is_local"]
            self.protectiongroups[stdout["items"][i]["name"]]["destroyed"] = stdout[
                "items"
            ][i]["destroyed"]
            self.protectiongroups[stdout["items"][i]["name"]]["host_count"] = stdout[
                "items"
            ][i]["host_count"]
            self.protectiongroups[stdout["items"][i]["name"]][
                "host_group_count"
            ] = stdout["items"][i]["host_group_count"]
            self.protectiongroups[stdout["items"][i]["name"]]["target_count"] = stdout[
                "items"
            ][i]["target_count"]
            self.protectiongroups[stdout["items"][i]["name"]]["pod"] = stdout["items"][
                i
            ]["pod"]
            self.protectiongroups[stdout["items"][i]["name"]][
                "snapshot_schedule"
            ] = stdout["items"][i]["snapshot_schedule"]
            self.protectiongroups[stdout["items"][i]["name"]][
                "replication_schedule"
            ] = stdout["items"][i]["replication_schedule"]
            self.protectiongroups[stdout["items"][i]["name"]][
                "source_retention"
            ] = stdout["items"][i]["source_retention"]
            self.protectiongroups[stdout["items"][i]["name"]][
                "target_retention"
            ] = stdout["items"][i]["target_retention"]
            self.protectiongroups[stdout["items"][i]["name"]]["volume_count"] = stdout[
                "items"
            ][i]["volume_count"]
            self.protectiongroups[stdout["items"][i]["name"]]["space"] = stdout[
                "items"
            ][i]["space"]
        return True

    def get_protectiongroupsnapshots(self):
        """
        Gets all networkports and updates `self.target-ports`.
        :returns: `True` for success, `False` on error.
        """
        path = "/protection-group-snapshots"
        response = self.client.get(path)
        if not self._check_result(response):
            return False
        self.protectiongroupsnapshots = {}
        stdout = self._get_json(response)
        for i in range(len(stdout["items"])):
            self.protectiongroupsnapshots[stdout["items"][i]["name"]] = {}
            self.protectiongroupsnapshots[stdout["items"][i]["name"]][
                "created"
            ] = stdout["items"][i]["created"]
            self.protectiongroupsnapshots[stdout["items"][i]["name"]][
                "destroyed"
            ] = stdout["items"][i]["destroyed"]
            self.protectiongroupsnapshots[stdout["items"][i]["name"]][
                "suffix"
            ] = stdout["items"][i]["suffix"]
            self.protectiongroupsnapshots[stdout["items"][i]["name"]][
                "time_remaining"
            ] = stdout["items"][i]["time_remaining"]
            self.protectiongroupsnapshots[stdout["items"][i]["name"]][
                "source"
            ] = stdout["items"][i]["source"]
            self.protectiongroupsnapshots[stdout["items"][i]["name"]]["pod"] = stdout[
                "items"
            ][i]["pod"]
            self.protectiongroupsnapshots[stdout["items"][i]["name"]][
                "eradication_config"
            ] = stdout["items"][i]["eradication_config"]
            self.protectiongroupsnapshots[stdout["items"][i]["name"]]["space"] = stdout[
                "items"
            ][i]["space"]
        return True

    def get_protectiongroupvolmembers(self):
        """
        Gets all volumes in protection-groups and updates `self.protectiongroupvolmembers`.
        :returns: `True` for success, `False` on error.
        """
        path = "/protection-groups/volumes"
        response = self.client.get(path)
        if not self._check_result(response):
            return False
        self.protectiongroupvolmembers = {}
        stdout = self._get_json(response)
        for i in range(len(stdout["items"])):
            if (
                stdout["items"][i]["group"]["name"]
                not in self.protectiongroupvolmembers.keys()
            ):
                self.protectiongroupvolmembers[stdout["items"][i]["group"]["name"]] = {}
                self.protectiongroupvolmembers[stdout["items"][i]["group"]["name"]][
                    "member"
                ] = []
            self.protectiongroupvolmembers[stdout["items"][i]["group"]["name"]][
                "member"
            ].append(stdout["items"][i]["member"])
        return True

    def get_pods(self):
        """
        Gets all pods and updates `self.pods`.
        :returns: `True` for success, `False` on error.
        """
        path = "/pods"
        response = self.client.get(path)
        if not self._check_result(response):
            return False
        self.pods = {}
        stdout = self._get_json(response)
        for i in range(len(stdout["items"])):
            self.pods[stdout["items"][i]["name"]] = {}
            self.pods[stdout["items"][i]["name"]]["id"] = stdout["items"][i]["id"]
            self.pods[stdout["items"][i]["name"]]["destroyed"] = stdout["items"][i][
                "destroyed"
            ]
            self.pods[stdout["items"][i]["name"]]["mediator"] = stdout["items"][i][
                "mediator"
            ]
            self.pods[stdout["items"][i]["name"]]["promotion_status"] = stdout["items"][
                i
            ]["promotion_status"]
            self.pods[stdout["items"][i]["name"]]["requested_promotion_state"] = stdout[
                "items"
            ][i]["requested_promotion_state"]
            self.pods[stdout["items"][i]["name"]]["failover_preferences"] = stdout[
                "items"
            ][i]["failover_preferences"]
            self.pods[stdout["items"][i]["name"]]["mediator_version"] = stdout["items"][
                i
            ]["mediator_version"]
            self.pods[stdout["items"][i]["name"]]["link_source_count"] = stdout[
                "items"
            ][i]["link_source_count"]
            self.pods[stdout["items"][i]["name"]]["link_target_count"] = stdout[
                "items"
            ][i]["link_target_count"]
            self.pods[stdout["items"][i]["name"]]["footprint"] = stdout["items"][i][
                "footprint"
            ]
            self.pods[stdout["items"][i]["name"]]["time_remaining"] = stdout["items"][
                i
            ]["time_remaining"]
            self.pods[stdout["items"][i]["name"]]["array_count"] = stdout["items"][i][
                "array_count"
            ]
            self.pods[stdout["items"][i]["name"]]["source"] = stdout["items"][i][
                "source"
            ]
            self.pods[stdout["items"][i]["name"]]["arrays"] = stdout["items"][i][
                "arrays"
            ]
            self.pods[stdout["items"][i]["name"]]["space"] = stdout["items"][i]["space"]
            self.pods[stdout["items"][i]["name"]]["eradication_config"] = stdout[
                "items"
            ][i]["eradication_config"]
        return True

    def get_remotepods(self):
        """
        Gets all pods and updates `self.pods`.
        :returns: `True` for success, `False` on error.
        """
        path = "/remote-pods"
        response = self.client.get(path)
        if not self._check_result(response):
            return False
        self.remotepods = {}
        stdout = self._get_json(response)
        for i in range(len(stdout["items"])):
            self.remotepods[stdout["items"][i]["name"]] = {}
            self.remotepods[stdout["items"][i]["name"]]["id"] = stdout["items"][i]["id"]
            self.remotepods[stdout["items"][i]["name"]]["arrays"] = stdout["items"][i][
                "arrays"
            ]
        return True

    def get_vol_name_by_devwwn(self, wwn):
        fetch_all_vol = self.get_volumes()
        if fetch_all_vol:
            for key, value in self.volumes.items():
                if value["serial"].lower() == wwn[-24:].lower():
                    return key
            return False


class SystemTask(PureConnection):
    def __init__(
        self, host: any, port: int, user: str, password: any, token: any, verify: bool
    ):
        super().__init__(host, port, user, password, token, verify)
        self.process = Process()

    def get_mountpoint_info(self, mountpoint=None):
        """
        Returns details of volume with WWN `wwn` or mounted on `mountpoint`.

        :param name: volume's `name`.
        :param mountpoint: `mountpoint` where the volume is mounted.
        :returns: str wwn, `None`, otherwise.
        """
        if mountpoint is None:
            return None

        if mountpoint is not None:
            mpath = self.process.get_mpath_from_mountpoint(mountpoint)
            if mpath is None:
                return None

            wwn = self.process.get_wwn_from_mpath(mpath)
            if wwn is None:
                return None

        return wwn

    def get_local_server_name_on_array(self):
        """Returns local server ID, or `None` on error."""
        hostname = self.process.get_hostname()
        server_name = hostname.split(".")[0]

        server_status = self.get_hosts(server_name)
        if not server_status:
            LOG.error(f"HOST: {server_name} API Call failed")
        return (server_name, self.hosts)

    def generate_clone_name(self, volume_name):
        """
        Generates a clone name from a volume name.

        :param volume_name: the volume name from which to generate a clone name.
        :returns: clone name, `None`, otherwise.
        """
        # remove clone name suffix from volume name
        original_name = re.sub(r"_\d+$", "", volume_name)

        # get list of volumes starting with 'orig_volname'
        self.get_volumes()
        lst = []
        for vol in self.volumes.values():
            if vol["name"].startswith(original_name):
                lst.append(vol["name"])

        if len(lst) == 0:
            # LOG.error('Clone name cannot be generated as no volumes is found.')
            return None

        # get indexes in the volume list
        volname_with_index = re.compile(r".*(_\d+)$")
        volindex_lst = [
            int(volname_.replace(f"{original_name}_", ""))
            for volname_ in lst
            if volname_with_index.match(volname_)
        ]
        volindex_lst.sort()
        if len(volindex_lst) == 0:
            clone_index = 1
        else:
            clone_index = volindex_lst[-1] + 1

        return f"{original_name}_{clone_index}"


class PureAdvanceConnection(SystemTask):
    # def run_volume_operation
    def create_volume(self, size: str, name: str) -> bool:
        """Create volume.

        Args:
            name (str): Name of the volume to be create on PureStorage Array
            size (str): Capacity of volume Eg: "1T", "300G", "20M"

        Returns:
            boolean: `True` for success, `False` on error.
        """
        path = "/volumes"
        data = {
            "names": name,
            "provisioned": totalbytes(size),
        }
        response = self.client.post(path, data)
        if not self._check_result(response):
            return False
        return True

    def delete_volume(self, name: str) -> bool:
        """Delete volume.

        Args:
            name (str): Name of the volume to be deleted on PureStorage Array

        Returns:
            boolean: `True` for success, `False` on error.
        """
        path = "/volumes"
        data = {
            "names": name,
            "destroyed": True,
        }
        response = self.client.patch(path, data)
        if not self._check_result(response):
            return False
        return True

    def connect_volume(self, hostname: str, volname: str, **kwargs) -> bool:
        """Connect volume.

        Args:
            hostname (str): Name of the host specified on PureStorage Array with which volume need to be connect
            volname (str): Name of the volume specified on PureStorage Array which need to be connect

        Returns:
            boolean: `True` for success, `False` on error.
        """
        path = "/connections"
        data = {
            "host_names": hostname,
            "volume_names": volname,
        }
        if kwargs["lunid"] is not None:
            data["lun"] = int(kwargs["lunid"])
        response = self.client.post(path, data)
        if not self._check_result(response):
            LOG.error(f"Failure : Connection of volume {volname} with {hostname}")
            return False
        return True

    def disconnect_volume(self, hostname: str, volname: str) -> bool:
        """Remove the connection of volume from .

        Args:
            hostname (str): Name of the host specified on PureStorage Array with which volume need to be connect
            volname (str): Name of the volume specified on PureStorage Array which need to be connect

        Returns:
            boolean: `True` for success, `False` on error.
        """
        path = "/connections"
        data = {
            "host_names": hostname,
            "volume_names": volname,
        }
        response = self.client.delete(path, data)
        if not self._check_result(response):
            return False
        return True

    def map_volume(self, name, mountpoint=None):
        """Map volume to local server and mount it to `mountpoint`.

        Args:
            name (str): Name of the volume to map to local server.
            mountpoint (str): Name of the volume to be deleted on PureStorage Array

        Returns:
            boolean: `True` for success, `False` on error.
        """
        # check if the volume exist
        volume_exist = self.get_volumes(name)
        if not volume_exist:
            LOG.error(f"Volume: {name} - doesnot exists on the Array")
            return False

        # check if mount point already used and get wwn number of the volume using this mountpoint
        vol_wwn = self.get_mountpoint_info(mountpoint)
        if vol_wwn is not None:
            LOG.error(f"Mount Point already in use by volume : {vol_wwn}")
            return False

        # check if the volume is already mapped to any servers
        vol_mappings = self.get_volumeconnections(name)
        if not vol_mappings:
            LOG.error(f"Volume: {name} API Call failed for connection validation")
            return False

        if bool(self.volumeconnections):
            LOG.error(f"Volume is already connected to: \n {self.volumeconnections}")
            return False

        # get local server details from the Pure Array and map the volume to it
        (hostname, server_name) = self.get_local_server_name_on_array()
        if not bool(server_name):
            LOG.error(f"{hostname} doesn't exist on the Array")
            return False

        # connect the volume to host
        if not self.connect_volume(hostname, name, lunid=None):
            return False

        # rescan scsi bus
        if not self.process.rescan_scsibus():
            return False

        # fetch the serialnumber of volume
        volume_detail = self.get_volumes(name)
        if volume_detail:
            dev_serial = self.volumes[name]["serial"]
        wwn = self.process.get_wwid_from_wwn(dev_serial)

        # add multipath alias of the volume
        if not self.process.add_multipath_alias(wwn):
            return False

        # reload multipath
        if not self.process.reload_multipathd():
            return False

        # if a mountpoint is specified, update fstab file and mount the volume
        if mountpoint is None:
            LOG.info("Mountpoint is not specified.")
            return True

        new_alias = self.process.get_mpath_from_wwn(wwn)
        if new_alias is not None:
            new_fsdevice = f"/dev/mapper/{new_alias}p1"
            if not self.process.add_entry_in_fstab(new_fsdevice, mountpoint):
                LOG.error("%s cannot be added to /etc/fstab", new_fsdevice)
                return False
            if not self.process.daemon_reload():
                return False
        else:
            LOG.error("Alias for the volume with WWN %s does not exist.", mountpoint)
            return False

        # mount target_mountpoint if it's not mounted
        # found it gets mounted after reload multipath, is it an expected behaviour?
        if not self.process.mountpoint_exists(mountpoint):
            if not self.process.mount(mountpoint):
                return False

        return True

    def unmap_volume(self, name=None, wwn=None):
        """
        Unmaps a Pure Storage volume with `WWN`. Unmounting the volume should be performed manually.

        :param wwn: `wwn` of the volume to unmap.
        :returns: `True` for success, `False` on error.
        """
        # check if volume name exists on Pure Storage
        if name:
            volume_exist = self.get_volumes(name)
            if not volume_exist:
                return False

        # fetch wwn number of the device if input is name
        if name:
            if volume_exist:
                dev_serial = self.volumes[name]["serial"]
            wwn = self.process.get_wwid_from_wwn(dev_serial)

        # check wwn of user input and fetch the name of the device
        if wwn:
            wwn = self.process.get_wwid_from_wwn(wwn)
            name = self.get_vol_name_by_devwwn(wwn)

        # Check if the host exist on the Pure Storage
        (hostname, server_name) = self.get_local_server_name_on_array()
        if not bool(server_name):
            LOG.error(f"{hostname} doesn't exist on the Pure Array")
            return False

        # check if the volume is already mapped to any servers
        vol_mappings = self.get_volumeconnections(name)
        if not vol_mappings:
            LOG.error(f"Volume: {name} API Call failed for connection validation")
            return False

        if not bool(self.volumeconnections):
            LOG.error(f"Volume {name} not connected with host {hostname}")
            return False

        # check if volume is visible to local server
        alias = self.process.get_mpath_from_wwn(wwn)
        if alias is None:
            return False

        # device_name variable declariation
        # To perform unmount and remove entry from fstab
        device_name = f"/dev/mapper/{alias}p1"

        # make sure volume is not mounted
        # unmount the filesystem if it is mounted
        if self.process.is_wwn_mounted(wwn) is not None:
            LOG.warning(
                "Volume with WWN %s is mounted on local server. Unmount it first.", wwn
            )
            mountpoint = self.process.get_mountpoint_from_devicename(device_name)
            if self.process.mountpoint_exists(mountpoint):
                if not self.process.umount(mountpoint):
                    return False

        # remove volume from fstab config file
        if self.process.is_device_in_fstab(device_name):
            if not self.process.remove_entry_from_fstab(device_name):
                return False
            if not self.process.daemon_reload():
                return False
        else:
            LOG.error("%s is not in /etc/fstab.", device_name)

        # remove (wwid, alias) entry from multipath.conf
        if not self.process.remove_multipath_entry(wwn, alias):
            return False

        # reload multipathd
        if not self.process.reload_multipathd():
            return False

        # delete raw devices of multipath device alias
        raw_devices = self.process.get_multipath_raw_devices(wwn)
        if raw_devices is None:
            LOG.warning(
                "No raw devices (%s) for multipath device %s.", raw_devices, alias
            )
        else:
            result_delete_rawdevs = []

            for rawdev in raw_devices:
                result = self.process.delete_raw_devices(rawdev)
                result_delete_rawdevs.append(result)

            if False in result_delete_rawdevs:
                LOG.error(
                    "Failed to delete the raw devices %s of %s. Result: %s.",
                    raw_devices,
                    alias,
                    result_delete_rawdevs,
                )
                return False

            LOG.info(
                "The raw devices %s of %s have been deleted. Result: %s.",
                raw_devices,
                alias,
                result_delete_rawdevs,
            )

        # reload multipathd
        if not self.process.reload_multipathd():
            return False

        # unmap the volume from the local server
        return self.disconnect_volume(hostname, name)

    def replace_volume(self, src_mountpoint, dst_mountpoint, unmount_src_mp):
        """
        Clones the volume mounted on `src_mountpoint` and mount it on `dst_mountpoint`,
        the volume that was mounted on `dst_mountpoint` will be deleted.

        :param src_mountpoint: mountpoint of the volume to be cloned.
        :param dst_mountpoint: mountpoint of the clone volume.
        :param unmount_src_mp: If True, unmount the source mountpoint, otherwise, not.
        :return: `True` for success, `False` on error.
        """
        # check details of vols on source and destination mountpoints
        # volume details: (wwn, volid, volname, volFolderName, volFolderId, scName)
        src_vol_wwn = self.get_mountpoint_info(mountpoint=src_mountpoint)
        if src_vol_wwn is None:
            return False

        dst_vol_wwn = self.get_mountpoint_info(mountpoint=dst_mountpoint)
        if dst_vol_wwn is None:
            return False

        # Fetch name from the wwn
        src_vol_name = self.get_vol_name_by_devwwn(src_vol_wwn)
        if not src_vol_name:
            return False
        dst_vol_name = self.get_vol_name_by_devwwn(dst_vol_wwn)
        if not dst_vol_name:
            return False

        # unmount the volume to be cloned, call it "the source volume"
        if unmount_src_mp:
            if not self.process.umount(src_mountpoint):
                return False

        # unmap the volume used by dst_mountpoint
        if not self.unmap_volume(dst_vol_name):
            return False

        # delete destination volume
        # TODO: with eradication
        if not self.delete_volume(dst_vol_name):
            return False

        # create a clone of source volume and mount it on dst_moutpoint
        clone_name = self.generate_clone_name(src_vol_name)
        if not self.clone_volume(clone_name, src_vol_name, dst_mountpoint):
            return False

        # mount source volume if needed
        if unmount_src_mp:
            if not self.process.mount(src_mountpoint):
                return False

        return True

    def create_host(self, iqn: str, name: str, personality: str) -> bool:
        """Create host.

        Args:
            name (str): Name of the Host to be create on PureStorage Array
            iqn (str): iqn of Host Eg: ""
            personality (str): personality of the host

        Returns:
            boolean: `True` for success, `False` on error.
        """
        personality_detail = personality if personality != "none" else None
        path = "/hosts"
        iqns = []
        data = {
            "names": name,
            "personality": personality_detail,
        }
        if iqn:
            iqns.append(iqn)
            data["iqns"] = iqns
        response = self.client.post(path, data)
        if not self._check_result(response):
            LOG.error(f"Host Creation Failed: {name}")
            return False
        return True

    def delete_host(self, name: str) -> bool:
        """Delete host.

        Args:
            name (str): Name of the host to be deleted on PureStorage Array

        Returns:
            boolean: `True` for success, `False` on error.
        """
        path = f"/hosts?names={name}"
        response = self.client.delete(path)
        if not self._check_result(response):
            return False
        return True

    def create_snapshot(self, name: str, suffix: str) -> bool:
        """Create Snapshot of the volume.

        Args:
            name (str): Name of the volume for which snapshot to be create on PureStorage Array
            suffix (str): suffix of the snapshot

        Returns:
            boolean: `True` for success, `False` on error.
        """
        path = "/volume-snapshots"
        data = {
            "source_names": name,
            "suffix": suffix,
        }
        response = self.client.post(path, data)
        if not self._check_result(response):
            return False
        return True

    def delete_snapshot(self, name: str) -> bool:
        """Delete snapshot.

        Args:
            name (str): Name of the snapshot to be deleted on PureStorage Array

        Returns:
            boolean: `True` for success, `False` on error.
        """
        path = "/volume-snapshots"
        data = {"names": name, "destroyed": True}
        response = self.client.patch(path, data)
        if not self._check_result(response):
            return False
        return True

    def clone_volume(self, cln_name: str, src_name: str, mt_pt: str = None) -> bool:
        """Create clone volume.

        Args:
            cln_name (str): Name of the clone volume to be create on PureStorage Array
            src_name (str): Name of the source volume for which clone need to be created on PureStorage Array

        Returns:
            boolean: `True` for success, `False` on error.
        """
        path = "/volumes"
        data = {
            "names": cln_name,
            "source": {"name": src_name},
        }

        # check if the volume name of clone exist
        volume_exist = self.get_volumes(cln_name)
        if volume_exist and self.volumes is not None:
            LOG.error(f'Clone volume "{cln_name}" already exists')
            return False

        # if mt_pt is provided then check otherwise create the clone volume
        if mt_pt:
            # Check the provided mountpoint is empty
            if not self.process.is_dir_empty(mt_pt):
                return False

            # Check the provided mountpoint exist
            if self.process.mountpoint_exists(mt_pt):
                return False

        # Create clone of the volume
        response = self.client.post(path, data)
        if not self._check_result(response):
            return False

        # if the mt_pt is provided and pre-check was fine then mount on the system.
        if mt_pt:
            self.map_volume(cln_name, mt_pt)

        return True
