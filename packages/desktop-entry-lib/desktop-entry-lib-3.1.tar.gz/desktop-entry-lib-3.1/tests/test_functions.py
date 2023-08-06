import desktop_entry_lib
import pathlib
import pytest
import sys
import os


def _touch_file(path: str) -> None:
    os.makedirs(os.path.dirname(path))
    f = open(path, "wb")
    f.close()


def test_version() -> None:
    assert isinstance(desktop_entry_lib.__version__, str)


def test_get_xdg_data_dirs() -> None:
    os.environ["XDG_DATA_DIRS"] = "/hello/world:/test/123:/foo/bar"
    assert desktop_entry_lib.get_xdg_data_dirs() == ["/hello/world", "/test/123", "/foo/bar"]

    os.environ["XDG_DATA_DIRS"] = "/hello/world:/test/123:/foo/bar:"
    assert desktop_entry_lib.get_xdg_data_dirs() == ["/hello/world", "/test/123", "/foo/bar"]

    os.environ.pop("XDG_DATA_DIRS")
    assert desktop_entry_lib.get_xdg_data_dirs() == [os.path.expanduser("~/.local/share"), "/usr/share"]


@pytest.mark.skipif(sys.platform == "win32", reason="Does not work with Windows Paths")
def test_get_icon_path(tmp_path: pathlib.Path) -> None:
    scalable_path = os.path.join(tmp_path, "icons", "hicolor", "scalable", "apps", "com.example.App.svg")
    normal_path = os.path.join(tmp_path, "icons", "hicolor", "128x128", "apps", "com.example.App.png")
    pixmaps_path = os.path.join(tmp_path, "pixmaps", "com.example.App.png")

    _touch_file(scalable_path)
    _touch_file(normal_path)
    _touch_file(pixmaps_path)

    os.environ["XDG_DATA_DIRS"] = str(tmp_path)

    assert desktop_entry_lib.get_icon_path("com.example.App") == str(scalable_path)

    os.remove(scalable_path)
    assert desktop_entry_lib.get_icon_path("com.example.App") == str(normal_path)

    os.remove(normal_path)
    assert desktop_entry_lib.get_icon_path("com.example.App") == str(pixmaps_path)

    os.remove(pixmaps_path)
    assert desktop_entry_lib.get_icon_path("com.example.App") is None


def test_is_action_identifier_valid() -> None:
    assert desktop_entry_lib.is_action_identifier_valid("hello") is True
    assert desktop_entry_lib.is_action_identifier_valid("hello-world") is True
    assert desktop_entry_lib.is_action_identifier_valid("hello_world") is False


def test_is_custom_key_name_valid() -> None:
    assert desktop_entry_lib.is_custom_key_name_valid("Hello") is False
    assert desktop_entry_lib.is_custom_key_name_valid("X-Hello") is True
    assert desktop_entry_lib.is_custom_key_name_valid("X-Hello-World") is True
    assert desktop_entry_lib.is_custom_key_name_valid("X-Hello_World") is False
    assert desktop_entry_lib.is_custom_key_name_valid("X-Hello-World[Lang]") is True
    assert desktop_entry_lib.is_custom_key_name_valid("X-Hello-World[Lang") is False
    assert desktop_entry_lib.is_custom_key_name_valid("X-Hello-World[]") is False
