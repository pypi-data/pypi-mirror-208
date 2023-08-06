import os
version_file = os.path.join(os.path.dirname(__file__), "kolibri", "VERSION")
Version=None
with open(version_file) as fh:
    Version = fh.read().strip()



