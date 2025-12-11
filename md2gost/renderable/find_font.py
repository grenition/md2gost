from sys import platform, exit
import subprocess
import logging
from functools import cache


def __find_font_linux(name: str, bold: bool, italic: bool):
    font_fallback_map = {
        "Times New Roman": ["Liberation Serif", "DejaVu Serif", "Times"],
        "Courier New": ["Liberation Mono", "DejaVu Sans Mono", "Courier"],
        "Arial": ["Liberation Sans", "DejaVu Sans", "Helvetica"],
    }
    
    search_names = [name]
    if name in font_fallback_map:
        search_names.extend(font_fallback_map[name])
    
    result = subprocess.run(
        "fc-list", shell=True, check=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        fonts = \
            [line.split(":") for line in result.stdout.strip().split("\n")]
        fonts = [font for font in fonts if len(font) == 3]
    else:
        logging.log(logging.ERROR, "fc-list not found")
        exit(1)

    for search_name in search_names:
        for path, names, styles in fonts:
            if (search_name in names
                    and ("Bold" in styles) == bool(bold)
                    and ("Italic" in styles) == bool(italic)):
                return path
    
    for search_name in search_names:
        for path, names, styles in fonts:
            if search_name in names:
                return path
    
    raise ValueError(f"Font {name} not found")


@cache
def find_font(name: str, bold: bool, italic: bool):
    if not name:
        raise ValueError("Invalid font")
    if platform == "linux":
        return __find_font_linux(name, bold, italic)
    else:
        from matplotlib.font_manager import findfont, FontProperties
        return findfont(FontProperties(
            family=name,
            weight="bold" if bold else "normal",
            style="italic" if italic else "normal"), fallback_to_default=False)


if __name__ == "__main__":
    print(find_font("Courier New", False, False))
