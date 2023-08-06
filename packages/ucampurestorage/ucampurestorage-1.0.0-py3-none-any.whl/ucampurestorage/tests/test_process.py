from unittest.mock import patch
import pytest
from ucampurestorage.lib.process import Process

# from pathlib import Path


@pytest.fixture
def init_ps() -> Process:
    return Process()


@pytest.mark.parametrize(
    "return_vals",
    [(0, "cs2.internal.admin.cam.ac.uk", None), (0, "cs-test.google.com", None)],
)
def test_process_hostname(init_ps, return_vals) -> None:
    returnval = return_vals
    with patch("ucampurestorage.lib.process.Process.run") as ps_run:
        ps_run.return_value = returnval
        hostname = init_ps.get_hostname()
        assert hostname == returnval[1]


@pytest.mark.parametrize(
    "return_vals, expected", [((0, "1", None), True), ((0, "2", None), False)]
)
def test_process_mountpoint_exists(init_ps, return_vals, expected) -> None:
    returnval = return_vals
    with patch("ucampurestorage.lib.process.Path.is_dir") as dir_ext:
        dir_ext.return_value = True
        with patch("ucampurestorage.lib.process.Process.run") as ps_run:
            ps_run.return_value = returnval
            mt_exist = init_ps.mountpoint_exists("/t1")
            assert mt_exist == expected


@pytest.mark.parametrize(
    "return_vals, mtpt, mt_check, expected",
    [
        ((0, "/dev/mapper/vold11p1", None), "/t1", True, "/dev/mapper/vold11p1"),
        ((1, "", None), "/t2", False, None),
    ],
)
def test_process_get_fsdevice_from_mountpoint(
    init_ps, return_vals, mtpt, mt_check, expected
) -> None:
    returnval = return_vals
    with patch("ucampurestorage.lib.process.Process.mountpoint_exists") as mt_check:
        mt_check.return_value = mt_check
        with patch("ucampurestorage.lib.process.Process.run") as ps_run:
            ps_run.return_value = returnval
            fsdev = init_ps.get_fsdevice_from_mountpoint(mtpt)
            assert fsdev == expected


@pytest.mark.parametrize(
    "return_val, expected",
    [
        ("/dev/mapper/vold11p1", "/dev/mapper/vold11"),
        ("/dev/mapper/vold8p1", "/dev/mapper/vold8"),
    ],
)
def test_process_get_mpath_from_mountpoint(init_ps, return_val, expected) -> None:
    returnval = return_val
    with patch(
        "ucampurestorage.lib.process.Process.get_fsdevice_from_mountpoint"
    ) as ps_run:
        ps_run.return_value = returnval
        fsdev = init_ps.get_mpath_from_mountpoint("/t1")
        assert fsdev == expected


@pytest.mark.skip
def test_process_get_wwn_from_mpath() -> None:
    pass


@pytest.mark.parametrize(
    "wwn, expected",
    [("6000d31000e39400000000000000029d", True), ("6000d31000e394000000000", False)],
)
def test_process_is_wwn_valid(init_ps, wwn, expected) -> None:
    valid_wwn = init_ps.is_wwn_valid(wwn)
    assert valid_wwn == expected


@pytest.mark.parametrize(
    "wwn, expected",
    [
        ("6000d31000e39400000000000000029d", True),
        ("6000d31000e30000000", False),
        ("6000d31000e3940000000001", True),
    ],
)
def test_process_is_wwn_serial_valid(init_ps, wwn, expected) -> None:
    valid_wwn = init_ps.is_wwn_serial_valid(wwn)
    assert valid_wwn == expected


@pytest.mark.parametrize(
    "return_val, wwn_mpath, wwn_valid, expected",
    [((0, "/d12", None), True, True, "/d12")],
)
def test_process_is_wwn_mounted(
    init_ps, wwn_mpath, wwn_valid, return_val, expected
) -> None:
    with patch("ucampurestorage.lib.process.Process.is_wwn_valid") as wwn_valid:
        wwn_valid.return_value = wwn_valid
        with patch(
            "ucampurestorage.lib.process.Process.get_mpath_from_wwn"
        ) as mpath_wwn:
            mpath_wwn.return_value = wwn_mpath
            with patch("ucampurestorage.lib.process.Process.run") as run:
                run.return_value = return_val
                is_mount = init_ps.is_wwn_mounted("6000d31000e39400000000000000029d")
                assert is_mount == expected


@pytest.mark.parametrize(
    "feed_list, expected", [([1, 2, 3], 4), ([1, 2, 4], 3), ([], 1)]
)
def test_process_get_index_in_list(init_ps, feed_list, expected) -> None:
    value_index = init_ps.get_index_in_list(feed_list)
    assert value_index == expected


@pytest.mark.parametrize(
    "return_val, expected",
    [
        ((0, "vold01\nvold02", None), "vold03"),
        ((0, "vold01\nvold03", None), "vold02"),
        ((0, "", None), "vold01"),
    ],
)
def test_process_generate_devicemapper_alias(init_ps, return_val, expected) -> None:
    with patch("ucampurestorage.lib.process.Process.run") as run:
        run.return_value = return_val
        value_index = init_ps.generate_devicemapper_alias()
        assert value_index == expected


@pytest.mark.parametrize(
    "device, expected",
    [
        ("/dev/mapper/vold05p1", True),
        ("/dev/mapper/vold05p2", False),
        ("/dev/mapper/pure", False),
    ],
)
def test_process_is_device_valid(init_ps, device, expected) -> None:
    value_index = init_ps.is_device_valid(device)
    assert value_index == expected


@pytest.mark.skip
def test_process_get_wwid_from_wwn() -> None:
    pass


@pytest.mark.parametrize(
    "fs, rc, expected", [("/dp1", (0, None), True), ("/dp2", (1, None), False)]
)
def test_process_mount(init_ps, fs, rc, expected):
    with patch("ucampurestorage.lib.process.Process.run") as run:
        run.return_value = rc
        mount_rt = init_ps.mount(fs)
        assert mount_rt == expected


@pytest.mark.parametrize(
    "fs, rc, expected", [("/dp1", (0, None), True), ("/dp2", (1, None), False)]
)
def test_process_unmount(init_ps, fs, rc, expected):
    with patch("ucampurestorage.lib.process.Process.run") as run:
        run.return_value = rc
        umount_rt = init_ps.umount(fs)
        assert umount_rt == expected


@pytest.mark.parametrize("version, expected", [("6", True), ("7", True), ("8", True)])
def test_process_reload_multipathd(init_ps, version, expected):
    with patch("ucampurestorage.lib.process.Process.get_release") as vers:
        vers.return_value = version
        with patch("ucampurestorage.lib.process.Process.run") as run:
            run.return_value = (0, None)
            reload_rt = init_ps.reload_multipathd()
            assert reload_rt == expected


@pytest.mark.parametrize("version, expected", [("6", True), ("7", True), ("8", True)])
def test_process_daemon_reload(init_ps, version, expected):
    with patch("ucampurestorage.lib.process.Process.get_release") as vers:
        vers.return_value = version
        with patch("ucampurestorage.lib.process.Process.run") as run:
            run.return_value = (0, None)
            reload_rt = init_ps.daemon_reload()
            assert reload_rt == expected


def test_process_get_multipath_raw_devices(init_ps):
    with patch("ucampurestorage.lib.process.Process.run") as run:
        run.return_value = (0, "sdj\nsdg\nsdi\nsdk", None)
        reload_rt = init_ps.get_multipath_raw_devices("5715765")
        assert reload_rt == ["sdj", "sdg", "sdi", "sdk"]


@pytest.mark.skip
def test_process_rescan_scsibus() -> None:
    pass
