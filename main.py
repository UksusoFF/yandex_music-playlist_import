import sys
import json
from YMusicImporter import YMusicImporter


def get_settings():
    with open("settings.json", "r") as read_file:
        return json.load(read_file)


if __name__ == "__main__":
    settings = get_settings()
    ya_client = YMusicImporter(**settings)
    ya_client.playlist_import(sys.argv[1])
