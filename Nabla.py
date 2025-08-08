import sublime
import sublime_plugin
from .core.color_utils import (
    PREFERENCES,
    storage_folder,
    check_and_apply_override
)
from .core.theme_activation import *
from .core.Icons import icons_package_installer

initial_color_scheme = None

def color_scheme_listener():
    global initial_color_scheme
    settings = sublime.load_settings(PREFERENCES)
    current_color_scheme = settings.get("color_scheme")
    if current_color_scheme != initial_color_scheme:
        initial_color_scheme = current_color_scheme
        check_and_apply_override()
    settings.clear_on_change("_color_scheme_listener")
    settings.add_on_change("_color_scheme_listener", color_scheme_listener)

def plugin_loaded():
    global initial_color_scheme
    settings = sublime.load_settings(PREFERENCES)
    initial_color_scheme = settings.get("color_scheme")
    settings.add_on_change("_color_scheme_listener", color_scheme_listener)
    icons_package_installer()

def plugin_unloaded():
    settings = sublime.load_settings(PREFERENCES)
    settings.clear_on_change("_color_scheme_listener")
    storage_folder()

class NablaActivateCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.display_list(THEMES)
    
    def display_list(self, themes):
        self.themes = themes
        self.initial_color_scheme = get_color_scheme()
        self.initial_ui_theme = get_ui_theme()
        quick_list = [theme for theme in self.themes]
        self.quick_list = quick_list
        self.window.show_quick_panel(
            quick_list, self.on_done, on_highlight=self.on_highlighted
        )

    def on_highlighted(self, index):
        preview_color_scheme(self._quick_list_to_scheme(index))
        preview_ui_theme(self._quick_list_to_theme(index))

    def on_done(self, index):
        if index is NO_SELECTION:
            revert_color_scheme(self.initial_color_scheme)
            revert_ui_theme(self.initial_ui_theme)
            return
        if index == 0:
            sublime.active_window().run_command("select_color_scheme")

        color_scheme = self._quick_list_to_scheme(index)
        activate_color_scheme(color_scheme)
        ui_theme = self._quick_list_to_theme(index)
        activate_ui_theme(ui_theme)

    def _quick_list_to_scheme(self, index):
        if index == 0:
            return "{}.sublime-color-scheme".format(C_SCHEME[0])
        return "{}.sublime-color-scheme".format(C_SCHEME[index - 1])

    def _quick_list_to_theme(self, index):
        return "{}.sublime-theme".format(THEMES[index])