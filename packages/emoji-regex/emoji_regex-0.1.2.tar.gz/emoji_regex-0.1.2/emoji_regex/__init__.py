import re
from importlib import resources

with resources.as_file(resources.files("emoji_regex") / "emoji_regex.bin") as path, open(path) as f:
    emoji_regex = re.compile(f.read().rstrip())
