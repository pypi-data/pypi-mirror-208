import pylistenbrainz
import musicbrainzngs

from .preferences import Preferences
from .constants import IMAGE_SIZE

class BrainzRequest:
    ''' Request and store user and image data from ListenBrainz and MusicBrainz '''

    def __init__(self, prefs: Preferences):

        self.lb_client = pylistenbrainz.ListenBrainz()

        print(f'Getting listening data for {prefs.username}...')
        self.releases = self._get_user_album_info(self.lb_client, prefs)
        if len(self.releases) != prefs.number:
            raise ValueError('ListenBrainz didn\' return enough data to proceed with!')

        print('Downloading the album art...')
        self.cover_images = [self._get_album_cover(release['release_mbid']) 
                             for release in self.releases]

    def _get_user_album_info(
        self, 
        client: pylistenbrainz.client.ListenBrainz, 
        prefs: Preferences
    ) -> dict:
        ''' Find the user's most listened albums in the given timespan '''

        response = client.get_user_releases(
            username=prefs.username,
            time_range=prefs.timespan,
            count=prefs.number,
        )
        releases = response['payload']['releases']

        return releases

    def _get_album_cover(self, mbid: str) -> bytes | None:
        ''' Download an album cover given a MusicBrainz ID (mbid) '''

        try:
            cover = musicbrainzngs.get_image_front(mbid, size=IMAGE_SIZE)
            return cover
        except musicbrainzngs.ResponseError as e:
            return None
