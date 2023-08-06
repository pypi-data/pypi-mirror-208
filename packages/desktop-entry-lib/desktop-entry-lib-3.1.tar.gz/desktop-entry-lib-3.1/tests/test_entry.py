import desktop_entry_lib
import pathlib
import pytest
import os


def _generate_test_entry() -> desktop_entry_lib.DesktopEntry:
    entry = desktop_entry_lib.DesktopEntry()
    entry.Type = "Application"
    entry.Version = "1.5"
    entry.Name.default_text = "Test"
    entry.Comment.default_text = "Hello"
    entry.Comment.translations["de"] = "Hallo"
    return entry


def test_should_show() -> None:
    if "XDG_CURRENT_DESKTOP" in os.environ:
        os.environ.pop("XDG_CURRENT_DESKTOP")

    entry = desktop_entry_lib.DesktopEntry()

    assert entry.should_show() is True

    entry.Hidden = True
    assert entry.should_show() is False

    entry.Hidden = False
    assert entry.should_show() is True

    entry.NotShowIn.append("TestDesktop")
    assert entry.should_show() is True

    os.environ["XDG_CURRENT_DESKTOP"] = "TestDesktop"
    assert entry.should_show() is False

    entry.NotShowIn.clear()

    entry.OnlyShowIn.append("HelloWorld")
    assert entry.should_show() is False

    os.environ["XDG_CURRENT_DESKTOP"] = "HelloWorld"
    assert entry.should_show() is True

    entry.Hidden = True
    assert entry.should_show() is False


def test_should_show_in_menu() -> None:
    entry = desktop_entry_lib.DesktopEntry()

    assert entry.should_show_in_menu() is True

    entry.NoDisplay = True
    assert entry.should_show_in_menu() is False

    entry.NoDisplay = False
    assert entry.should_show_in_menu() is True


def test_is_empty() -> None:
    entry = desktop_entry_lib.DesktopEntry()
    assert entry.is_empty() is True
    entry.Name.default_text = "Test"
    assert entry.is_empty() is False


def test_from_string() -> None:
    entry = desktop_entry_lib.DesktopEntry.from_string("[Desktop Entry]\nType=Application\nName=Test\nExec=prog")
    assert entry.Name.default_text == "Test"
    assert entry.Exec == "prog"


def test_invalid_desktop_entry_exception() -> None:
    with pytest.raises(desktop_entry_lib.InvalidDesktopEntry):
        desktop_entry_lib.DesktopEntry.from_string("Hello")


def test_from_file(tmp_path: pathlib.Path) -> None:
    entry = _generate_test_entry()
    entry.write_file(os.path.join(tmp_path, "com.example.App.desktop"))
    assert entry == desktop_entry_lib.DesktopEntry.from_file(os.path.join(tmp_path, "com.example.App.desktop"))


def test_from_id(tmp_path: pathlib.Path) -> None:
    entry = _generate_test_entry()
    os.environ["XDG_DATA_DIRS"] = str(tmp_path)
    entry.write_file(os.path.join(tmp_path, "applications", "com.example.App.desktop"))
    assert entry == desktop_entry_lib.DesktopEntry.from_id("com.example.App")


def test_equals() -> None:
    entry = _generate_test_entry()
    assert entry == entry
    assert not entry == desktop_entry_lib.DesktopEntry()
    assert not entry == 42


def test_get_keywords() -> None:
    entry = _generate_test_entry()
    assert isinstance(entry.get_keywords(), list)
    assert isinstance(desktop_entry_lib.DesktopEntry.get_keywords(), list)
