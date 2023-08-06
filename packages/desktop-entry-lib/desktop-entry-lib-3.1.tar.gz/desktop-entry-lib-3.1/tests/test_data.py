import desktop_entry_lib
import pathlib


DATA_DIR = pathlib.Path(__file__).parent / "data"


def test_data_equals() -> None:
    for i in DATA_DIR.iterdir():
        if i.suffix != ".desktop":
            continue

        assert desktop_entry_lib.DesktopEntry.from_file(i) == desktop_entry_lib.DesktopEntry.from_file(i)


def test_data_jdtextedit() -> None:
    entry = desktop_entry_lib.DesktopEntry.from_file(DATA_DIR / "com.gitlab.JakobDev.jdTextEdit.desktop")
    assert entry.Version == "1.5"
    assert entry.Type == "Application"
    assert entry.Name.default_text == "jdTextEdit"
    assert entry.Comment.default_text == "An advanced text editor"
    assert entry.Comment.translations["de"] == "Ein erweiterter Texteditor"
    assert entry.Exec == "jdTextEdit"
    assert entry.Icon == "com.gitlab.JakobDev.jdTextEdit"
    assert entry.Terminal is False
    assert entry.StartupNotify is False
    assert entry.Categories == ["TextEditor", "Development", "Qt"]
    assert entry.SingleMainWindow is True
    assert entry.MimeType == ["text/plain"]


def test_data_firefox() -> None:
    entry = desktop_entry_lib.DesktopEntry.from_file(DATA_DIR / "org.mozilla.firefox.desktop")
    assert entry.Version == "1.0"
    assert entry.Type == "Application"
    assert entry.Name.default_text == "Firefox Web Browser"
    assert entry.Comment.default_text == "Browse the World Wide Web"
    assert entry.Comment.translations["de"] == "Im Internet surfen"
    assert entry.Exec == "/usr/bin/flatpak run --branch=stable --arch=x86_64 --command=firefox --file-forwarding org.mozilla.firefox @@u %u @@"
    assert entry.Icon == "org.mozilla.firefox"
    assert entry.Terminal is False
    assert entry.StartupNotify is True
    assert entry.Categories == ["Network", "WebBrowser"]
    assert entry.SingleMainWindow is None
    assert entry.MimeType == ["text/html", "text/xml", "application/xhtml+xml", "application/vnd.mozilla.xul+xml", "text/mml", "x-scheme-handler/http", "x-scheme-handler/https"]
    assert entry.Keywords.default_list == ["web", "browser", "internet"]
    assert entry.StartupWMClass == "firefox"
    assert entry.CustomKeys["X-Flatpak"] == "org.mozilla.firefox"
    assert entry.Actions["new-window"].Name.default_text == "Open a New Window"
    assert entry.Actions["new-window"].Name.translations["de"] == "Neues Fenster"
    assert entry.Actions["new-window"].Icon is None
    assert entry.Actions["new-window"].Exec == "/usr/bin/flatpak run --branch=stable --arch=x86_64 --command=firefox --file-forwarding org.mozilla.firefox --new-window @@u %u @@"


def test_data_flatseal() -> None:
    entry = desktop_entry_lib.DesktopEntry.from_file(DATA_DIR / "com.github.tchx84.Flatseal.desktop")
    assert entry.Version is None
    assert entry.Type == "Application"
    assert entry.Name.default_text == "Flatseal"
    assert entry.Comment.default_text == "Manage Flatpak permissions"
    assert entry.Comment.translations["de"] == "Berechtigungen von Flatpak-Anwendungen verwalten"
    assert entry.Exec == "/usr/bin/flatpak run --branch=stable --arch=x86_64 --command=com.github.tchx84.Flatseal com.github.tchx84.Flatseal"
    assert entry.Icon == "com.github.tchx84.Flatseal"
    assert entry.Terminal is False
    assert entry.StartupNotify is True
    assert entry.Categories == ["Utility"]
    assert entry.SingleMainWindow is None
    assert entry.MimeType == []
    assert entry.Keywords.default_list == ["seal", "sandbox"]
    assert entry.Keywords.translations["de"] == ["Siegel", "seal", "Sandkasten", "sandbox"]
    assert entry.CustomKeys["X-Purism-FormFactor"] == "Workstation;Mobile;"
    assert entry.CustomKeys["X-Flatpak"] == "com.github.tchx84.Flatseal"


def test_data_dolphin() -> None:
    entry = desktop_entry_lib.DesktopEntry.from_file(DATA_DIR / "org.kde.dolphin.desktop")
    assert entry.Version is None
    assert entry.Type == "Application"
    assert entry.Name.default_text == "Dolphin"
    assert entry.Comment.default_text == ""
    assert entry.GenericName.default_text == "File Manager"
    assert entry.GenericName.translations["de"] == "Dateiverwaltung"
    assert entry.Exec == "dolphin %u"
    assert entry.Icon == "system-file-manager"
    assert entry.Terminal is False
    assert entry.StartupNotify is None
    assert entry.Categories == ["Qt", "KDE", "System", "FileTools", "FileManager"]
    assert entry.SingleMainWindow is None
    assert entry.MimeType == ["inode/directory"]
    assert entry.StartupWMClass == "dolphin"
    assert entry.Keywords.default_list == ["files", "file management", "file browsing", "samba", "network shares", "Explorer", "Finder"]
    assert entry.Keywords.translations["de"] == ["Dateien", "Dateiverwaltung", "Netzwerkfreigaben"]
    assert entry.CustomKeys["X-DocPath"] == "dolphin/index.html"
    assert entry.CustomKeys["X-DBUS-ServiceName"] == "org.kde.dolphin"
    assert entry.CustomKeys["X-KDE-Shortcuts"] == "Meta+E"
