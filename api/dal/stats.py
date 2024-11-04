import os
import json

# check if running in docker
if os.path.exists("/.dockerenv"):
    FILE_PATH = os.path.join("/etc/stats", "stats.txt")
else:
    FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "volume", "stats.txt")

class StatsDAL:
    def __init__(self):
        self.file_path = FILE_PATH

    def get_stats(self):
        # if the file does not exist, create it
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as file:
                file.write(json.dumps({}, indent=4))

        with open(self.file_path, 'r') as file:
            return json.load(file)

    def update_stats(self, stats):
        with open(self.file_path, 'w') as file:
            file.write(json.dumps(stats, indent=4))
