# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
import functools

NO_SELECTION = -1
PREFERENCES = "Preferences.sublime-settings"
THEMES = ["Nabla Adaptive", "Nabla Dark", "Nabla Light"]
C_SCHEME = ["Nabla One Dark", "Nabla One Light"]

def get_color_scheme():
    return sublime.load_settings(PREFERENCES).get("color_scheme", "")


def set_color_scheme(path):
    return sublime.load_settings(PREFERENCES).set("color_scheme", path)


def preview_color_scheme(path):
    set_color_scheme(path)


def activate_color_scheme(path):
    set_color_scheme(path)
    commit()


def revert_color_scheme(path):
    set_color_scheme(path)


def get_ui_theme():
    return sublime.load_settings(PREFERENCES).get("theme", "")


def set_ui_theme(path):
    return sublime.load_settings(PREFERENCES).set("theme", path)


def preview_ui_theme(path):
    set_ui_theme(path)


def activate_ui_theme(path):
    set_ui_theme(path)
    commit()


def revert_ui_theme(path):
    set_ui_theme(path)


def commit():
    return sublime.save_settings(PREFERENCES)