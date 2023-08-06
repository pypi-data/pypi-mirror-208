import desktop_entry_lib
import pathlib
import shutil
import os


DATA_DIR = pathlib.Path(__file__).parent / "data"


def _create_test_directory(path: pathlib.Path) -> None:
    first = desktop_entry_lib.DesktopEntry()
    first.Name.default_text = "First"
    first.Categories.append("Office")
    first.MimeType.append("text/plain")
    first.Hidden = True
    first.write_file(os.path.join(path, "com.example.First.desktop"))

    second = desktop_entry_lib.DesktopEntry()
    second.Name.default_text = "Second"
    second.Categories.append("Internet")
    second.NoDisplay = True
    second.write_file(os.path.join(path, "com.example.Second.desktop"))

    third = desktop_entry_lib.DesktopEntry()
    third.Name.default_text = "Third"
    third.Categories.append("Internet")
    third.write_file(os.path.join(path, "com.example.Third.desktop"))


def test_data_collection() -> None:
    collection = desktop_entry_lib.DesktopEntryCollection()
    collection.load_directory(DATA_DIR)
    for i in os.listdir(DATA_DIR):
        if not i.endswith(".desktop"):
            continue

        desktop_id = i.removesuffix(".desktop")

        assert desktop_id in collection
        assert desktop_id in collection.desktop_entries


def test_menu_collection(tmp_path: pathlib.Path) -> None:
    collection_menu = desktop_entry_lib.DesktopEntryCollection()
    collection_data = desktop_entry_lib.DesktopEntryCollection()

    shutil.copytree(DATA_DIR, os.path.join(tmp_path, "applications"))
    os.environ["XDG_DATA_DIRS"] = str(tmp_path)
    collection_menu.load_menu()

    collection_data.load_directory(DATA_DIR)

    assert collection_menu == collection_data


def test_get_entries_by_category(tmp_path: pathlib.Path) -> None:
    _create_test_directory(tmp_path)

    collection = desktop_entry_lib.DesktopEntryCollection()
    collection.load_directory(tmp_path)

    assert desktop_entry_lib.DesktopEntry.from_file(os.path.join(tmp_path, "com.example.First.desktop")) in collection.get_entries_by_category("Office")
    assert desktop_entry_lib.DesktopEntry.from_file(os.path.join(tmp_path, "com.example.Second.desktop")) in collection.get_entries_by_category("Internet")
    assert desktop_entry_lib.DesktopEntry.from_file(os.path.join(tmp_path, "com.example.Third.desktop")) in collection.get_entries_by_category("Internet")


def test_get_visible_entries(tmp_path: pathlib.Path) -> None:
    _create_test_directory(tmp_path)

    collection = desktop_entry_lib.DesktopEntryCollection()
    collection.load_directory(tmp_path)

    assert desktop_entry_lib.DesktopEntry.from_file(os.path.join(tmp_path, "com.example.First.desktop")) not in collection.get_visible_entries()
    assert desktop_entry_lib.DesktopEntry.from_file(os.path.join(tmp_path, "com.example.Second.desktop")) in collection.get_visible_entries()
    assert desktop_entry_lib.DesktopEntry.from_file(os.path.join(tmp_path, "com.example.Third.desktop")) in collection.get_visible_entries()


def test_get_menu_entries(tmp_path: pathlib.Path) -> None:
    _create_test_directory(tmp_path)

    collection = desktop_entry_lib.DesktopEntryCollection()
    collection.load_directory(tmp_path)

    assert desktop_entry_lib.DesktopEntry.from_file(os.path.join(tmp_path, "com.example.First.desktop")) not in collection.get_menu_entries()
    assert desktop_entry_lib.DesktopEntry.from_file(os.path.join(tmp_path, "com.example.Second.desktop")) not in collection.get_menu_entries()
    assert desktop_entry_lib.DesktopEntry.from_file(os.path.join(tmp_path, "com.example.Third.desktop")) in collection.get_menu_entries()


def test_length(tmp_path: pathlib.Path) -> None:
    _create_test_directory(tmp_path)

    collection = desktop_entry_lib.DesktopEntryCollection()
    collection.load_directory(tmp_path)

    assert len(collection) == 3


def test_contains(tmp_path: pathlib.Path) -> None:
    _create_test_directory(tmp_path)

    collection = desktop_entry_lib.DesktopEntryCollection()
    collection.load_directory(tmp_path)

    assert "com.example.First" in collection
    assert "com.example.Second" in collection
    assert "com.example.Third" in collection
    assert "com.example.Fourth" not in collection
