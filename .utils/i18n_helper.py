import os
import subprocess

# Add the path to msgfmt.exe (adjust as needed)
gettext_bin = r"C:\Program Files\gettext-iconv\bin"
env = os.environ.copy()
env["PATH"] = gettext_bin + os.pathsep + env["PATH"]

subprocess.run(
    ["django-admin", "compilemessages"],
    cwd=r"C:\Users\Ali\Desktop\micro\micro",
    env=env
)