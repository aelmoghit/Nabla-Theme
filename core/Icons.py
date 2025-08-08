"""
Pckage Icons Installer
"""

import os
import sublime

sublime.active_window().settings().set("status_icn", False)

ICONS_PACKAGE = {
    "icons1": "A File Icon",
    "icons2": "Zukan Icon Theme",
    "icons3": "FileIcons",
}
PKGCTRL_SETTINGS = "Package Control.sublime-settings"
THEME_NAME = os.path.splitext(os.path.basename(os.path.dirname(__file__)))[0]

MSG = """\
<div id="afi-installer">
    <style>
        #afi-installer {{
            padding: 1rem;
            line-height: 1.5;
            max_width:800;
        }}
        #afi-installer code {{
            background-color: color(var(--background) blend(var(--foreground) 80%));
            line-height: 1;
            padding: 0.25rem;
        }}
        #afi-installer code a {{
            font-size:23px;
            text-decoration:underline
        }}
        #afi-installer a {{
            padding: 0;
            margin: 0;
        }}
        #packages {{
            max_width: 800;
            padding:5px 10px;
            text-align: center;
            white-space: wrap
        }}
        #packages a {{
            font-weight: bold;
            padding: 0 10px;
            text-decoration:none
        }}
    </style>
    <h2 style="margin-top:0px">Install Icons Package 📦</h2>

    <span style="font-weight:bold">{}</span> requires 
    <code><var>A File Icon<a href="open_url/icons1" title="more details">+</a></var></code> 
    or <code><var>Zukan Icon Theme<a href="open_url/icons2" title="more details">+</a></var></code>
    or <code><var>FileIcons<a href="open_url/icons3" title="more details">+</a></var></code> 
    package for enhanced support of the file-specific icons.

    <br><br>Would you like to install?
    <br><div id="packages">
    <a href="install/icons1">A File Icon</a>  
    <a href="install/icons2">Zukan Icon Theme</a> 
    <a href="install/icons3">FileIcons</a> 
    </div>
    <a href="cancel" style="color:red;">Cancel</a>
</div>
""".format(
    THEME_NAME.replace("-", " ").upper()
)


def is_installed():
    pkgctrl_settings = sublime.load_settings(PKGCTRL_SETTINGS)
    installed_packages = set(pkgctrl_settings.get("installed_packages", []))
    return any(pkg in installed_packages for pkg in ICONS_PACKAGE.values())


def on_navigate(href):
    if href.startswith("install/"):
        install(href.replace("install/", ""))
    if href.startswith("open_url/"):
        discover(href.replace("open_url/", ""))
    if href == "cancel":
        hide()
        hide()


def install(pkg):
    print("Installing `{}` ...".format(ICONS_PACKAGE[pkg]))
    sublime.active_window().run_command(
        "install_packages", {"packages": [ICONS_PACKAGE[pkg]]}
    )
    hide()


def discover(pkg):
    sublime.active_window().run_command(
        "open_url", {"url": "https://packagecontrol.io/packages/" + ICONS_PACKAGE[pkg]}
    )


def hide():
    sublime.active_window().settings().set("status_icn", True)
    sublime.active_window().active_view().hide_popup()


def reload():
    status = sublime.active_window().settings().get("status_icn")
    if not status:
        return plugin_loaded
    return None

def icons_package_installer():
    from package_control import events
    
    if events.install(THEME_NAME) and not is_installed():
        window = sublime.active_window()
        view = window.active_view()
        window.focus_view(view)
        row = int(view.rowcol(view.visible_region().a)[0] + 1)
        view.show_popup(
            MSG,
            flags=16,
            location=view.text_point(row, 5),
            max_width=800,
            max_height=800,
            on_navigate=on_navigate,
            on_hide=reload(),
        )