"""Create an installable .ankiaddon without development files."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parent
output = root / 'dist' / 'button-colors.ankiaddon'
output.parent.mkdir(exist_ok=True)
with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
    for path in sorted((root / 'button_colors_plus').iterdir()):
        if path.suffix in {'.py', '.json', '.md'}:
            archive.write(path, path.name)
print(output)
