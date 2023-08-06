# desktop-entry-lib

![PyPI](https://img.shields.io/pypi/v/desktop-entry-lib)
![PyPI - Downloads](https://img.shields.io/pypi/dm/desktop-entry-lib)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/desktop-entry-lib)
![PyPI - License](https://img.shields.io/pypi/l/desktop-entry-lib)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/desktop-entry-lib)
![Read the Docs](https://img.shields.io/readthedocs/desktop-entry-lib)

desktop-entry-lib allows reading and writing .desktop files according to the [Desktop Entry Specification](https://specifications.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html)

```python
import desktop_entry_lib


def write() -> None:
    entry = desktop_entry_lib.DesktopEntry()

    entry.Name.default_text = "My App"
    entry.Comment.default_text = "A short description"
    entry.Comment.translations["de"] = "A short german description"
    entry.Type = "Application"
    entry.Exec = "my-app"

    entry.write_file("my_app.desktop")


def read() -> None:
    entry = desktop_entry_lib.DesktopEntry.from_file("my_app.desktop")

    print("Name: " + entry.Name.default_text)
    print("Comment: " + entry.Comment.default_text)
    print("German translation for Comment: " + entry.Comment.translations.get("de", "None"))
    print("Type: " + entry.Type)
    print("Exec: " + entry.Exec)


if __name__ == "__main__":
    write()
    read()
```

Features:
- Fully static typed
- No external dependencies
- Full Documentation and Examples available
- Support running inside a [Flatpak](https://flatpak.org)
- The whole lib is a single file
- Supports [PyPy](https://www.pypy.org)

[Read the documentation](https://desktop-entry-lib.readthedocs.io)


