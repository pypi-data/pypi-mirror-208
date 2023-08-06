import sys
import json
import logging
import getpass
from argparse import ArgumentParser, ArgumentTypeError, Action
from ucampurestorage.lib.tokencreater import TokenCreater as token
from ucampurestorage.lib.pureconnect import PureConnection as PureStorage
from ucampurestorage.lib.pureconnect import PureAdvanceConnection as PureAdvance
from ucampurestorage import VERSION

LOG = logging.getLogger(__name__)


class LoadFromFile(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        with values as f:
            args = json.load(f)

        for k, v in args.items():
            setattr(namespace, k, v)


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise ArgumentTypeError("Boolean value expected.")


class Options:
    def __init__(self):
        self._init_parser()

    def _init_parser(self):
        """Define arguments for the CLI."""
        self.parser = ArgumentParser(
            description="Manage Pure Storage Manager objects via REST API."
        )
        self.parser.add_argument("-v", "--version", action="version", version=VERSION)
        self.parser.add_argument(
            "--storage",
            default="uis-pure-wcdc1.srv.uis.private.cam.ac.uk",
            type=str,
            help="Pure hostname. Default: uis-pure-wcdc1.srv.uis.private.cam.ac.uk",
        )
        self.parser.add_argument("--port", default=443, help="Pure port. Default: 443")
        self.parser.add_argument(
            "--client_id", type=str, help="Pure Storage Client ID for API"
        )
        self.parser.add_argument(
            "--key_id", type=str, help="Pure Storage Key ID for API"
        )
        self.parser.add_argument(
            "--client_name", type=str, help="Pure Storage Client Name for API"
        )
        self.parser.add_argument("--user", type=str, help="Pure Storage username")
        self.parser.add_argument("--password", type=str, help="Pure Storage password")
        self.parser.add_argument(
            "--is_secure",
            type=str2bool,
            default=False,
            help="Secure connection. Default: False",
        )
        self.parser.add_argument(
            "--record_config",
            type=str2bool,
            default=False,
            help="Record multipath and file system config details.\
                                 Default: False (do not record system config details)",
        )
        self.parser.add_argument(
            "--file",
            type=open,
            action=LoadFromFile,
            help="Read arguments from json file",
        )
        self.parser.add_argument(
            "--keyfile",
            type=str,
            help="path to private keys inorder to generate token for the API call",
        )
        self.subparsers = self.parser.add_subparsers(dest="subparser")
        self.parser_tokengen = self.subparsers.add_parser(
            "tokengen",
            help='Generate Pure Storage API token to access objects. \
                                                      Example: ucampurestorage tokengen --keyfile "./key.pem"',
        )
        self.parser_tokengen.add_argument(
            "-inkeyfile",
            "--newkeyfile",
            type=str,
            help="path to the new private key location to make pure storage call",
        )
        self.parser_tokengen.add_argument(
            "-out",
            "--outputfile",
            type=str,
            help="path and file name to generate token file in json as output",
        )
        self.parser_list = self.subparsers.add_parser("list", help="List Pure objects.")
        self.parser_list.add_argument(
            "--object",
            required=True,
            choices=[
                "arrays",
                "controllers",
                "hosts",
                "volumes",
                "volumegroups",
                "hostgroups",
                "volumesnapshots",
                "targetports",
                "networkports",
                "volumeconnections",
                "protectiongroups",
                "protectiongroupsnapshots",
                "protectiongroupvolmembers",
                "pods",
                "remotepods",
            ],
        )
        self.parser_list.add_argument(
            "--format",
            choices=["json"],
            help="Format of the output. Supported formats: json",
        )
        self.parser_volume_operations = self.subparsers.add_parser(
            "volume", help="Operations with respect to volumes in the Pure objects."
        )
        self.volumeoperation = self.parser_volume_operations.add_subparsers(
            dest="volumeoperation"
        )
        self.listvol = self.volumeoperation.add_parser(
            "list", help="list a Volume details"
        )
        self.listvol.add_argument(
            "--name",
            required=True,
            help="Detail information of the volume on Pure Array.",
        )
        self.listvol.add_argument(
            "--format",
            required=False,
            help="Detail information of the volume on Pure Array.",
        )
        self.createvol = self.volumeoperation.add_parser("create", help="create Volume")
        self.createvol.add_argument(
            "--size",
            required=True,
            help="Size of the volume to be created on Pure Array.",
        )
        self.createvol.add_argument(
            "--name",
            required=False,
            help="Name of the volume to be created on Pure Array.",
        )
        self.deletevol = self.volumeoperation.add_parser("delete", help="delete Volume")
        self.deletevol.add_argument(
            "--name",
            required=True,
            help="Name of the volume to be deleted on Pure Array.",
        )
        self.deletevol.add_argument(
            "-nop", "--no_prompt", required=False, action="store_true"
        )
        self.connectvol = self.volumeoperation.add_parser(
            "connect", help="Connect Volume to Host"
        )
        self.connectvol.add_argument(
            "--hostname",
            required=True,
            help="Name of the host specified on Pure Array for initiators to which the volume has to be mapped.",
        )
        self.connectvol.add_argument(
            "--volname",
            required=True,
            help="Name of the volume to be connected to the host initiators on Pure Array.",
        )
        self.connectvol.add_argument(
            "--lunid",
            help="HOSTID need to be assigned for the volume while the  host initiators on Pure Array.",
        )
        self.disconnectvol = self.volumeoperation.add_parser(
            "disconnect", help="disconnect Volume from Host"
        )
        self.disconnectvol.add_argument(
            "--hostname",
            required=True,
            help="Name of the host specified on Pure Array for initiators to which the volume has to be unmapped.",
        )
        self.disconnectvol.add_argument(
            "--volname",
            required=True,
            help="Name of the volume to be disconnect from the host initiators of Pure Array.",
        )
        self.mapvol = self.volumeoperation.add_parser(
            "map",
            help="Maps the volume to local server and \
                                                      mounts it on the specified mount point.",
        )
        self.mapvol.add_argument(
            "--name", required=True, help="Name of the volume to map to local server."
        )
        self.mapvol.add_argument(
            "--mp",
            required=False,
            help="OPTIONAL. If specified, it is the path of the mountpoint \
                                            to mount the volume on. Otherwise, no mount attempt will take place.",
        )
        self.unmapvol = self.volumeoperation.add_parser(
            "unmap",
            help="Unmaps the volume from local server and \
                                                      Volume must be unmounted.",
        )
        self.unmapvol.add_argument(
            "--name",
            required=False,
            help="Name of the volume to unmap from local server.",
        )
        self.unmapvol.add_argument(
            "--wwn",
            required=False,
            help="WWN of the volume to unmap from local server.",
        )
        self.replacevol = self.volumeoperation.add_parser(
            "replace",
            help="Clone the volume mounted on source mountpoint and mount it on destination mountpoint. \
                Then, delete the volume was initially mounted on destination mountpoint. ",
        )
        self.replacevol.add_argument(
            "--src_mp",
            required=True,
            help="Source mountpoint. Must be on local server.",
        )
        self.replacevol.add_argument(
            "--dst_mp",
            required=True,
            help="Destination mountpoint. Must be on local server.",
        )
        self.replacevol.add_argument(
            "--unmount_src_mp",
            type=str2bool,
            default=True,
            help="Optional. If False, do not unmount the source mountpoint. \
                                        Defaults to True",
        )
        self.clonevol = self.volumeoperation.add_parser(
            "clone",
            help="Create a snapshot with label of a volume with WWN, create a view volume from the snapshot, \
                then, map the view volume to local server and  mount it on target mountpoint.",
        )
        self.clonevol.add_argument(
            "--name",
            required=True,
            help="Name of the new volume to create",
        )
        self.clonevol.add_argument(
            "--srcvol",
            metavar="Source Volume",
            required=True,
            help="Source Volume for which need to be cloned.",
        )
        self.clonevol.add_argument(
            "--target_mp",
            metavar="Target Mount Point",
            required=False,
            help="The mountpoint that the view volume will be mounted on. \
                Must be on local server Eg: /d01",
        )
        self.parser_host_operations = self.subparsers.add_parser(
            "host", help="Operations with respect to hosts in the Pure objects."
        )
        self.hostoperation = self.parser_host_operations.add_subparsers(
            dest="hostoperation"
        )
        self.listhost = self.hostoperation.add_parser(
            "list", help="list a host details"
        )
        self.listhost.add_argument(
            "--name",
            required=True,
            help="Detail information of the host on Pure Array.",
        )
        self.listhost.add_argument(
            "--format",
            required=False,
            help="Detail information of the host on Pure Array.",
        )
        self.createhost = self.hostoperation.add_parser("create", help="create Volume")
        self.createhost.add_argument(
            "--iqn", required=False, help="IQN of the host to be created on Pure Array."
        )
        self.createhost.add_argument(
            "--name",
            required=True,
            help="Name of the host to be created on Pure Array.",
        )
        self.createhost.add_argument(
            "--personality",
            required=False,
            default="none",
            choices=[
                "aix",
                "esxi",
                "hpux",
                "solaris",
                "vms",
                "oracle-vm-server",
                "none",
            ],
            help="Personality of the host to be created on Pure Array.",
        )
        self.deletehost = self.hostoperation.add_parser("delete", help="delete host")
        self.deletehost.add_argument(
            "--name",
            required=True,
            help="Name of the host to be deleted on Pure Array.",
        )
        self.deletehost.add_argument(
            "-nop", "--no_prompt", required=False, action="store_true"
        )
        self.parser_snapshot_operations = self.subparsers.add_parser(
            "snapshot", help="Operations with respect to snapshots in the Pure objects."
        )
        self.snapoperation = self.parser_snapshot_operations.add_subparsers(
            dest="snapoperation"
        )
        self.listsnap = self.snapoperation.add_parser(
            "list", help="list a snapshots of the volume"
        )
        self.listsnap.add_argument(
            "--volname",
            required=True,
            help="information of the snapshot of the volume on Pure Array.",
        )
        self.listsnap.add_argument(
            "--format",
            required=False,
            help="information of the snapshot on Pure Array in json. Ex: --format=json",
        )
        self.createsnap = self.snapoperation.add_parser(
            "create", help="Create a snapshots of the volume"
        )
        self.createsnap.add_argument(
            "--srcvol",
            required=True,
            help="name of the volume for which snapshot need to be captured on Pure Array.",
        )
        self.createsnap.add_argument(
            "--suffix",
            required=True,
            help="suffix of the snapshot of the volume on Pure Array.",
        )
        self.deletesnap = self.snapoperation.add_parser(
            "delete", help="delete a snapshots of the volume"
        )
        self.deletesnap.add_argument(
            "--snapname",
            required=True,
            help="name of the snapshot need to be deleted on Pure Array.",
        )

    def parse(self, args=None):
        """Parse given arguments and execute an action accordingly."""
        result = None
        self.known, self.unknown = self.parser.parse_known_args(args)[:]
        if len(self.unknown) != 0:
            LOG.error(
                f"Specified parameter is not suitable: \n \t \t \t \t {self.unknown}"
            )
            return False

        def _checkuserparms(data: dict):
            for key, value in data.items():
                if getattr(self.known, key) is None:
                    inputvalue = input(f"{value}: ")
                    setattr(self.known, key, inputvalue)

        check_dict = {
            "user": "Username",
            "client_id": "Client ID",
            "key_id": "Key ID",
            "client_name": "Client Name",
            "keyfile": "Private file location",
        }

        _checkuserparms(check_dict)

        if self.known.password is None:
            self.known.password = getpass.getpass()

        result = run_option(self.known.subparser, self.known)
        return result


def _token_object(args):
    token_obj = token()
    if token_obj.current_token is None:
        if hasattr(args, "outputfile"):
            token_obj.token_generation(
                args.client_id,
                args.key_id,
                args.client_name,
                args.keyfile,
                args.user,
                args.storage,
                args.password,
                args.outputfile,
            )
        else:
            token_obj.token_generation(
                args.client_id,
                args.key_id,
                args.client_name,
                args.keyfile,
                args.user,
                args.storage,
                args.password,
                None,
            )
    return token_obj


def create_token(args):
    """
    Generate Pure Storage token.

    Example: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd>
        --client_name=<ClientName> --keyfile="privatekey.pem"  tokengen
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json  tokengen
    """
    token_obj = _token_object(args)
    LOG.info(f"\nAccess token for {args.client_name}:\n\n{token_obj.current_token}")


def run_option(subparser, args):
    """
    Runs a ucampurestorage subcommand.
    :param subparser: the subcommand to run.
    :param args: args to pass to the ucampurestorage subcommand.
    :return: result of the executed subcommand.
    """
    function_switcher = {
        "tokengen": create_token,
        "list": list_object,
        "volume": volume_operations,
        "host": host_operations,
        "snapshot": snap_operations,
    }
    subcommand_func = function_switcher.get(subparser)
    return subcommand_func(args) if subcommand_func is not None else None


def list_object(args):
    """
    List Pure Storage objects.

    Example: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd>
        --client_name=<ClientName> --keyfile=".\\privatekey.pem" list --object controllers
    Example: ucampurestorage --file=./ucampurestorage/lib/secrets.json list --object controllers
    Example: ucampurestorage --file=./ucampurestorage/lib/secrets.json list --object controllers --format=json
    """
    token_obj = _token_object(args)
    PureObj = PureStorage(
        args.storage,
        args.port,
        args.user,
        args.password,
        token_obj.current_token,
        args.is_secure,
    )
    (result, data) = PureObj.run_list_object(args.object)
    if not result or data is None:
        return result
    if args.format is None:
        LOG.info(
            f"List of {args.object}: \n{chr(10).join(str(item) for item in data.items())}"
        )
        return result
    if args.format == "json":
        LOG.info(
            f"List of {args.object}:\n {json.dumps(data, indent=4, sort_keys=False)}"
        )


def volume_operations(args):
    """
    Perform Pure Storage volume level Operations.

    Example: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd> \
        --client_name=<ClientName> --keyfile="privatekey.pem"  volume {list,create,delete,connect,\
                                        disconnect,map,unmap,replace,clone}
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json  volume {list,create,delete,\
                                        connect,disconnect,map,unmap,replace,clone}
    """
    volume_operations = {
        "list": detail_volume,
        "create": create_volume,
        "connect": connect_volume,
        "disconnect": disconnect_volume,
        "map": map_volume,
        "unmap": unmap_volume,
        "delete": delete_volume,
        "replace": replace_volume,
        "clone": clone_volume,
    }
    subcommand_func = volume_operations.get(args.volumeoperation)
    return subcommand_func(args) if subcommand_func is not None else None


def host_operations(args):
    """
    Perform Pure Storage host level Operations.

    Example: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd>
        --client_name=<ClientName> --keyfile="privatekey.pem"  host {list,create,delete}
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json  host {list,create,delete}
    """
    host_operations = {
        "list": detail_host,
        "create": create_host,
        "delete": delete_host,
    }
    subcommand_func = host_operations.get(args.hostoperation)
    return subcommand_func(args) if subcommand_func is not None else None


def snap_operations(args):
    """
    Perform Pure Storage Snapshot level Operations.

    Example: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd>
        --client_name=<ClientName> --keyfile="privatekey.pem"  snapshot {list,create,delete}
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json  snapshot {list,create,delete}
    """
    snap_operations = {
        "list": list_snapshots,
        "create": create_snapshot,
        "delete": delete_snapshot,
    }
    subcommand_func = snap_operations.get(args.snapoperation)
    return subcommand_func(args) if subcommand_func is not None else None


def detail_host(args):
    """
    List the detail information of the host connected to the  Pure Storage.

    Example 1: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd> \
        --client_name=<ClientName> --keyfile="privatekey.pem"  host  list  --name cs-dev-db2
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json  host list --name cs-dev-db2
    Example 3: ucampurestorage --file=./ucampurestorage/lib/secrets.json  host list --name cs-dev-db2 --format=json
    """
    token_obj = _token_object(args)
    PureObj = PureAdvance(
        args.storage,
        args.port,
        args.user,
        args.password,
        token_obj.current_token,
        args.is_secure,
    )
    result = PureObj.get_hosts(args.name)
    data = PureObj.hosts
    if not result or data is None:
        return result
    if args.format is None:
        LOG.info(
            f"Details of {args.name}: \n{chr(10).join(str(item) for item in data.items())}"
        )
        return result
    if args.format == "json":
        LOG.info(
            f"Details of {args.name}:\n {json.dumps(data, indent=4, sort_keys=False)}"
        )
        return result


def create_host(args):
    """Create host defination on the Purestorage.

    Example 1: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd> \
        --client_name=<ClientName> --keyfile="privatekey.pem"  host  create  --name <HOSTNAME> --iqn <IQN number>\
            --personality <aix,esxi,hpux,solaris,vms,oracle-vm-server,none>
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json host create --name <HOSTNAME> \
            --iqn <IQN number> --personality <aix,esxi,hpux,solaris,vms,oracle-vm-server,none>
    """
    token_obj = _token_object(args)
    PureObj = PureAdvance(
        args.storage,
        args.port,
        args.user,
        args.password,
        token_obj.current_token,
        args.is_secure,
    )
    result = PureObj.create_host(args.iqn, args.name, args.personality)
    if result:
        LOG.info(
            f'Successfully "{args.name}" created : "{args.iqn}" with personality "{args.personality}"'
        )
    else:
        LOG.error(f'Failure in creation: "{args.name}" !!')
    return result


def delete_host(args):
    """Delete host defination on the Pure Storage.

    Example 1: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd> \
        --client_name=<ClientName> --keyfile="privatekey.pem"  host  delete  --name <HOSTNAME>
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json host delete --name <HOSTNAME>
    """
    token_obj = _token_object(args)
    PureObj = PureAdvance(
        args.storage,
        args.port,
        args.user,
        args.password,
        token_obj.current_token,
        args.is_secure,
    )
    if not args.no_prompt:
        valid_inputs = ["y", "yes", "n", "no"]
        invalid = True
        while invalid:
            validate_deletion = input(
                f"Are you sure you want to delete {args.name} [Y/N](yes/no) : "
            )
            user_entry = validate_deletion.lower()
            if user_entry in valid_inputs and user_entry in valid_inputs[:2]:
                result = PureObj.delete_host(args.name)
                if result:
                    LOG.info(f"Successfully {args.name} deleted !!")
                    invalid = False
                    return True
                else:
                    LOG.error(f"Failed in {args.name} deleted !!")
                    return False
            elif user_entry in valid_inputs and user_entry in valid_inputs[2:]:
                LOG.warning(f"Deletion of {args.name} has been cancelled !!")
                invalid = False
            else:
                LOG.error(f"{user_entry} is invalide input")
    else:
        result = PureObj.delete_host(args.name)
        if result:
            LOG.info(f"Successfully {args.name} deleted !!")
        else:
            LOG.error(f"Failed in deletion of Volume : {args.name}")
        return result


def detail_volume(args):
    """
    List the detail information of the volume from the  Pure Storage.

    Example 1: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd>
        --client_name=<ClientName> --keyfile="privatekey.pem"  volume  list  --name TEST113
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json  volume list  --name TEST113
    Example 3: ucampurestorage --file=./ucampurestorage/lib/secrets.json  volume list  --name TEST113 --format=json
    """
    token_obj = _token_object(args)
    PureObj = PureAdvance(
        args.storage,
        args.port,
        args.user,
        args.password,
        token_obj.current_token,
        args.is_secure,
    )
    result = PureObj.get_volumes(args.name)
    data = PureObj.volumes
    if not result or data is None:
        return result
    if args.format is None:
        LOG.info(
            f"Details of {args.name}: \n{chr(10).join(str(item) for item in data.items())}"
        )
        return result
    if args.format == "json":
        LOG.info(
            f"Details of {args.name}:\n {json.dumps(data, indent=4, sort_keys=False)}"
        )
        return result


def create_volume(args):
    """Create Volume on the Pure storage.

    Example 1: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd>
        --client_name=<ClientName> --keyfile="privatekey.pem"  volume  create  --name TEST113 --size 1T
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json  volume create  --name TEST113 --size 1T
    """
    token_obj = _token_object(args)
    PureObj = PureAdvance(
        args.storage,
        args.port,
        args.user,
        args.password,
        token_obj.current_token,
        args.is_secure,
    )
    result = PureObj.create_volume(args.size, args.name)
    if result:
        LOG.info(f"Successfully {args.name} created : {args.size}")
    else:
        LOG.error(f"Failure in {args.name} created")
    return result


def delete_volume(args):
    """Delete Volume from the Pure storage.

    Example 1: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd>
        --client_name=<ClientName> --keyfile="privatekey.pem"  volume  delete  --name TEST113
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json  volume delete  --name TEST113
    """
    token_obj = _token_object(args)
    PureObj = PureAdvance(
        args.storage,
        args.port,
        args.user,
        args.password,
        token_obj.current_token,
        args.is_secure,
    )
    if not args.no_prompt:
        valid_inputs = ["y", "yes", "n", "no"]
        invalid = True
        while invalid:
            validate_deletion = input(
                f"Are you sure you want to delete {args.name} [Y/N](yes/no) : "
            )
            user_entry = validate_deletion.lower()
            if user_entry in valid_inputs and user_entry in valid_inputs[:2]:
                result = PureObj.delete_volume(args.name)
                if result:
                    LOG.info(f"Successfully {args.name} deleted !!")
                    invalid = False
                else:
                    LOG.error(f"Failed in deletion of Volume : {args.name}")
                return result
            elif user_entry in valid_inputs and user_entry in valid_inputs[2:]:
                LOG.warning(f"Deletion of {args.name} has been cancelled !!")
                invalid = False
            else:
                LOG.error(f"{user_entry} is invalid input")
    else:
        result = PureObj.delete_volume(args.name)
        if result:
            LOG.info(f"Successfully {args.name} deleted !!")
        else:
            LOG.error(f"Failed in deletion of Volume : {args.name}")
        return result


def connect_volume(args):
    """Connect Volume to the host on the Pure storage.

    Example 1: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd>
        --client_name=<ClientName> --keyfile="privatekey.pem"  volume  connect --hostname HOST01 --volname TEST113
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json  volume connect  \
        --hostname HOST01 --volname TEST113
    [optionally define the LUNID]
    Example 3: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd>
        --client_name=<ClientName> --keyfile="privatekey.pem"  volume  connect --hostname HOST01 --volname \
            TEST113 --lunid 77
    Example 4: ucampurestorage --file=./ucampurestorage/lib/secrets.json  volume connect  --hostname HOST01 \
        --volname TEST113  --lunid 77
    """
    token_obj = _token_object(args)
    PureObj = PureAdvance(
        args.storage,
        args.port,
        args.user,
        args.password,
        token_obj.current_token,
        args.is_secure,
    )
    result = PureObj.connect_volume(args.hostname, args.volname, lunid=args.lunid)
    if result:
        LOG.info(f"connections of {args.volname} to initiator {args.hostname}")
    else:
        LOG.error(
            f"failure in connections of {args.volname} to initiator {args.hostname}"
        )
    return result


def disconnect_volume(args):
    """Disconnect Volume from the host on the Pure storage.

    Example 1: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd>
        --client_name=<ClientName> --keyfile="privatekey.pem"  volume  disconnect --hostname HOST01 --volname TEST113
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json volume disconnect \
            --hostname HOST01 --volname TEST113
    """
    token_obj = _token_object(args)
    PureObj = PureAdvance(
        args.storage,
        args.port,
        args.user,
        args.password,
        token_obj.current_token,
        args.is_secure,
    )
    result = PureObj.disconnect_volume(args.hostname, args.volname)
    if result:
        LOG.info(
            f"connections removed of {args.volname} from initiator {args.hostname}"
        )
    else:
        LOG.error(
            f"failure in connections removal of {args.volname} from initiator {args.hostname}"
        )
    return result


def replace_volume(args):
    """Replace the mounted clone volume with new clone from Pure storage and mount to the local server.

    Example 1: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd>
        --client_name=<ClientName> --keyfile="privatekey.pem" volume replace --src_mp /t1  --dst_mp /t2
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json volume replace --src_mp /t1  --dst_mp /t2
    """
    token_obj = _token_object(args)
    PureObj = PureAdvance(
        args.storage,
        args.port,
        args.user,
        args.password,
        token_obj.current_token,
        args.is_secure,
    )
    result = PureObj.replace_volume(args.src_mp, args.dst_mp, args.unmount_src_mp)
    if result:
        LOG.info(f"replace the volume {args.src_mp} with {args.dst_mp}")
    else:
        LOG.error(f"failed the replace the volume {args.src_mp} with {args.dst_mp}")
    return result


def clone_volume(args):
    """Clone volume on Pure storage and mount to the local server.

    Example 1: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd>
        --client_name=<ClientName> --keyfile="privatekey.pem" volume clone --name TEST113_clone --srcvol \
            TEST113 --target_mp /t2
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json volume clone --name TEST113_clone \
        --srcvol TEST113 --target_mp /t2
    """
    token_obj = _token_object(args)
    PureObj = PureAdvance(
        args.storage,
        args.port,
        args.user,
        args.password,
        token_obj.current_token,
        args.is_secure,
    )
    result = PureObj.clone_volume(args.name, args.srcvol, args.target_mp)
    if result:
        if args.target_mp:
            LOG.info(
                f"Cloned  volume {args.name} of {args.srcvol} created to be mounted on {args.target_mp}."
            )
        else:
            LOG.info(f"Cloned  volume {args.name} of {args.srcvol} created.")
    return result


def list_snapshots(args):
    """
    List the detail information of the snapshot from the  Pure Storage.

    Example: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd>
        --client_name=<ClientName> --keyfile="privatekey.pem"  snapshot list --volname TEST12
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json  snapshot list --volname TEST12
    Example 3: ucampurestorage --file=./ucampurestorage/lib/secrets.json  snapshot list --volname TEST12  --format=json
    """
    token_obj = _token_object(args)
    PureObj = PureAdvance(
        args.storage,
        args.port,
        args.user,
        args.password,
        token_obj.current_token,
        args.is_secure,
    )
    result = PureObj.get_volumesnapshots(args.volname)
    data = PureObj.volumesnapshots
    if not result or data is None:
        return result
    if args.format is None:
        LOG.info(
            f"Snapshot of Volume {args.volname}: \n{chr(10).join(str(item) for item in data.items())}"
        )
    if args.format == "json":
        LOG.info(
            f"Snapshot of Volume {args.volname}:\n {json.dumps(data, indent=4, sort_keys=False)}"
        )
    return result


def create_snapshot(args):
    """Create snapshot of the volume on the Pure storage.

    Example 1: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd>
        --client_name=<ClientName> --keyfile="privatekey.pem" snapshot create --srcvol TEST113 --suffix snap01
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json  snapshot create \
            --srcvol TEST113 --suffix snap01
    """
    token_obj = _token_object(args)
    PureObj = PureAdvance(
        args.storage,
        args.port,
        args.user,
        args.password,
        token_obj.current_token,
        args.is_secure,
    )
    result = PureObj.create_snapshot(args.srcvol, args.suffix)
    if result:
        LOG.error(
            f"Snapshot of the volume {args.srcvol} created : {args.srcvol}.{args.suffix}"
        )
    else:
        LOG.error(
            f"Failure in Snapshot of the volume {args.srcvol}: {args.srcvol}.{args.suffix}"
        )
    return result


def delete_snapshot(args):
    """Delete snapshot of the volume on the Pure storage.

    Example 1: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd>
        --client_name=<ClientName> --keyfile="privatekey.pem" snapshot delete --snapname TEST113.snap01
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json  snapshot delete --snapname TEST113.snap01
    """
    token_obj = _token_object(args)
    PureObj = PureAdvance(
        args.storage,
        args.port,
        args.user,
        args.password,
        token_obj.current_token,
        args.is_secure,
    )
    result = PureObj.delete_snapshot(args.snapname)
    if result:
        LOG.info(f"Deletion of the snapshot {args.snapname}")
    else:
        LOG.error(f"Failure in deletion of the snapshot : {args.snapname}")
    return result


def map_volume(args):
    """Map volume to the local server which  is provided by Pure storage.

    Example 1: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd>
        --client_name=<ClientName> --keyfile="privatekey.pem" volume map --name TEST113 --mp /t2
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json volume map --name TEST113 --mp /t2
    """
    token_obj = _token_object(args)
    PureObj = PureAdvance(
        args.storage,
        args.port,
        args.user,
        args.password,
        token_obj.current_token,
        args.is_secure,
    )
    result = PureObj.map_volume(args.name, args.mp)
    if result:
        LOG.info(f"mapping of {args.name} to mountpoint {args.mp}")
    else:
        LOG.error(f"Fail in mapping of {args.name} to mountpoint {args.mp}")
    return result


def unmap_volume(args):
    """Map volume to the local server which  is provided by Pure storage.

    Example 1: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd>
        --client_name=<ClientName> --keyfile="privatekey.pem" volume unmap --name TEST113
    Example 2: ucampurestorage --file=./ucampurestorage/lib/secrets.json volume unmap --name TEST113
    [optionally define the LUNID]
    Example 3: ucampurestorage --client_id=<clientID> --key_id=<KeyID> --user=<User> --password=<passwd>
        --client_name=<ClientName> --keyfile="privatekey.pem" volume unmap --wwn <WWN number>
    Example 4: ucampurestorage --file=./ucampurestorage/lib/secrets.json volume unmap --wwn <WWN number>
    """
    token_obj = _token_object(args)
    PureObj = PureAdvance(
        args.storage,
        args.port,
        args.user,
        args.password,
        token_obj.current_token,
        args.is_secure,
    )
    result = PureObj.unmap_volume(args.name, args.wwn)
    if result:
        LOG.info(f"Successfully unmapping of {args.wwn}")
    else:
        LOG.error(f"failure in unmapping of {args.wwn}")
    return result


if __name__ == "__main__":
    obj = Options()
    obj.parse(sys.argv[1:])
