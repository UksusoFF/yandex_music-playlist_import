import io
import os
import time
import eyed3
from yandex_music.client import Client


class YMusicImporter:
    def __init__(self, email, password):
        self.client = Client.from_credentials(email, password, **{'report_new_fields': False})
        self.email = email

    def output(self, string):
        print(string)
        with open('log.log', 'a', encoding='utf-8') as f:
            f.write(string + '\n')

    def playlist_import(self, path):
        self.output('Start import playlist from {}'.format(path))

        self.playlist_create(
            os.path.basename(path),
            self.playlist_parse(path)
        )

        self.output('Import completed')

    def playlist_parse(self, path):
        items = []

        eyed3.log.setLevel("ERROR")

        with io.open(path, encoding='utf-8') as playlist:
            for file in playlist.readlines():
                audio = eyed3.load(os.path.normpath(file.strip().replace('\ufeff', '')))
                items.append("{}".format(" - ".join([
                    audio.tag.artist,
                    audio.tag.title
                ])))

        return items

    def playlist_create(self, title, items):
        playlist = self.client.users_playlists_create(title)

        self.output("https://music.yandex.ru/users/" + playlist.owner.login + "/playlists/" + str(playlist.kind))

        for i, track in enumerate(items):
            track_number = i + 1

            if i % 50 == 0 and i != 0:
                print("Waiting 5 minutes for prevent RPS limit")
                time.sleep(60 * 5)

            try:
                res = self.client.search(text=track, type_="track")

                time.sleep(1)

                if res and res.tracks:
                    founded = res.tracks.results[0]

                    playlist = self.client.users_playlists_insert_track(
                        kind=playlist.kind,
                        track_id=founded.id,
                        album_id=founded.albums[0].id,
                        revision=playlist.revision,
                        at=playlist.track_count,
                        timeout=60
                    )

                    founded_artist = str(', '.join(list(map(lambda x: x.name, founded.artists))))

                    founded_str = "{}".format(" - ".join([
                        founded_artist,
                        str(founded.title),
                    ]))

                    self.output("{}. {}{}".format(
                        track_number,
                        track,
                        " => [" + founded_str + "]" if res and res.tracks else " => [Not found] ")
                    )

                    time.sleep(1)
            except Exception as e:
                self.output("{}. {}{}".format(track_number, track, str(e)))
