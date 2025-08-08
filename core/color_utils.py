import sublime
import re
import os
import colorsys
import json
import plistlib
from collections import OrderedDict
from coloraide import Color

SFOLDER_NAME = "NablaSchemes"
PREFERENCES = "Preferences.sublime-settings"
THEME_BACKGROUNDS = {
    "Nabla Dark.sublime-theme": "#242936",
    "Nabla Light.sublime-theme": "color(#fcfcfc a(0.58))",
}
DEFAULT_LIGHT_SCHEMES = [
    "Breakers.sublime-color-scheme",
    "Celeste.sublime-color-scheme",
    "Sixteen.sublime-color-scheme"
]
IGNORED_SCHEMES = [
    "Nabla One Dark.sublime-color-scheme",
    "Nabla One Light.sublime-color-scheme"
]


def check_scheme_bg(scheme_path):
    try:
        path = scheme_path[scheme_path.find("Packages") :]
        scheme_content = sublime.decode_value(sublime.load_resource(path))
        if scheme_content.get("globals", {}).get("background"):
            return path
        return None
    except Exception as e:
        print(f"Error reading color scheme: {e}")
        return None

def get_scheme_content(color_scheme):
    """Load color scheme content with proper path handling."""
    try:
        # First try loading as resource (for built-in schemes)
        content = sublime.load_resource(color_scheme)
        if content:
            return color_scheme
    except:
        pass

    try:
        # Handle paths for both Packages/ and direct paths
        if color_scheme.startswith("Packages/"):
            rel_path = color_scheme[9:]
        else:
            rel_path = color_scheme
        # Convert to platform-specific path
        rel_path = rel_path.replace("/", os.sep)
        # Search in all package directories
        packages_path = sublime.packages_path()
        installed_path = sublime.installed_packages_path()
        list_package = os.listdir(packages_path)
        list_package.remove("User")
        # Check installed packages (.sublime-package files)
        if installed_path:
            for pkg_file in os.listdir(installed_path):
                if pkg_file.endswith('.sublime-package'):
                    try:
                        import zipfile
                        with zipfile.ZipFile(os.path.join(installed_path, pkg_file)) as z:
                            matches = [path for path in z.namelist() if path.find(rel_path) != -1]
                            if matches:
                                return [os.path.join(installed_path, pkg_file)] + matches
                    except:
                        continue
        # Check regular package directories
        for package_dir in [
            os.path.join(packages_path, d) for d in list_package
        ]:
            scheme_path = os.path.join(package_dir, rel_path)
            bg_exsit = check_scheme_bg(scheme_path) if os.path.exists(scheme_path) else ''
            if bg_exsit:
                return bg_exsit
            for p in os.listdir(package_dir):
                scheme_path = os.path.join(package_dir, p, rel_path)
                bg_exsit = check_scheme_bg(scheme_path) if os.path.exists(scheme_path) else ''
                if bg_exsit:
                    return bg_exsit
    except:
        pass
    return None

def extract_background_color(scheme_path):
    """Reads a .sublime-color-scheme file using Sublime's parser"""
    if type(scheme_path) is list:
        import zipfile
        with zipfile.ZipFile(scheme_path[0]) as z:
            try:
                color_data = sublime.decode_value(z.read(scheme_path[1]).decode('utf-8'))
                return color_data.get("globals", {}).get("background")
            except Exception as e:
                print(f"Error reading color scheme: {e}")
                return None
    try:
        # Load & parse with Sublime's JSON decoder (supports comments)
        color_data = sublime.decode_value(sublime.load_resource(scheme_path))
        return color_data.get("globals", {}).get("background")
    except Exception as e:
        print(f"Error reading color scheme: {e}")
        return None

def parse_color(color_str, scheme_path: None):
    """Parse color string into RGB tuple."""
    if type(scheme_path) is list:
        import zipfile
        with zipfile.ZipFile(scheme_path[0]) as z:
            try:
                color_data = sublime.decode_value(z.read(scheme_path[1]).decode('utf-8'))
            except Exception as e:
                print(f"Error reading color scheme: {e}")
    else:
        color_data = sublime.decode_value(sublime.load_resource(scheme_path))

    color_str = color_str.strip().lower()
    variables = color_data.get("variables", {})
    if color_str.startswith("var("):
        var_name = color_str[4:-1].strip()
        return variables.get(var_name, "")
    # Handle color modification functions
    if color_str.startswith("color("):
        return handle_color_modification(color_str, scheme_path)
    return color_str

def handle_color_modification(color_expr, scheme_path):
    # Extract the base color and modifications
    base_match = re.match(r"color\(([^)]+)\)", color_expr)
    if not base_match:
        return None
    parts = [p.strip() for p in base_match.group(1).split(" ") if p.strip()]
    if not parts:
        return None
    base_color = parse_color(parts[0], scheme_path)
    if not base_color:
        return None
    return base_color


def storage_folder(rm=False):
    user_path = os.path.join(sublime.packages_path(), "User", SFOLDER_NAME)
    os.makedirs(user_path, exist_ok=True)
    # clear subfolder
    for scheme in os.listdir(user_path):
        file_path = os.path.join(user_path, scheme)
        if os.path.isfile(file_path):
            os.remove(file_path)
    if rm and os.path.exists(user_path):
        os.rmdir(user_path)
        return
    return user_path

def get_scheme_filename(scheme_path):
    return os.path.basename(scheme_path).replace(".sublime-color-scheme", "")

def is_light_scheme(color_scheme):
    """Check if current color scheme is light."""
    if not color_scheme:
        return False
    if color_scheme in DEFAULT_LIGHT_SCHEMES:
        return True
    scheme_content = get_scheme_content(color_scheme)
    bg_color = extract_background_color(scheme_content)
    if not bg_color:
        return False
    rgb = parse_color(bg_color, scheme_content)
    if not rgb:
        return False
    luminance = Color.luminance(Color(rgb))
    return luminance > 0.5

def apply_override(scheme_path, background_color):
    """Create override file with requested structure and background color."""
    if not scheme_path or not scheme_path.endswith(".sublime-color-scheme"):
        return
    scheme_name = get_scheme_filename(scheme_path)
    user_path = storage_folder()
    override_path = os.path.join(user_path, scheme_name + ".sublime-color-scheme")
    override_content = OrderedDict(
        [
            ("variables", {}),
            ("globals", OrderedDict([
                ("background", background_color),
                ("gutter", background_color)
            ])),
            ("rules", []),
        ]
    )
    try:
        with open(override_path, "w", encoding="utf-8") as f:
            json.dump(override_content, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("[ColorSchemeOverride] Error writing override: {}".format(e))

def check_and_apply_override():
    settings = sublime.load_settings("Preferences.sublime-settings")
    current_theme = settings.get("theme")
    current_scheme = settings.get("color_scheme")
    if current_theme not in THEME_BACKGROUNDS:
        storage_folder(True)
        return
    intended_background = THEME_BACKGROUNDS[current_theme]
    theme_is_dark = current_theme == "Nabla Dark.sublime-theme"
    scheme_is_light = is_light_scheme(current_scheme)
    
    if theme_is_dark and not scheme_is_light:
        apply_override(current_scheme, intended_background)
    elif not theme_is_dark and scheme_is_light:
        apply_override(current_scheme, intended_background)