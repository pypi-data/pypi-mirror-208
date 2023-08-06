import io
from PIL import Image, ImageDraw, ImageFont
import datetime
import os

from .preferences import Preferences
from .constants import IMAGE_SIZE

class ImageProcessing:
    ''' Turn the album art from MusicBrainz into a collage and save it to a file '''

    def create_collage(
        self, 
        prefs: Preferences, 
        images: list[bytes], 
        releases: list[str],
    ) -> bytes:
        ''' Compile the images from bytes with pillow '''
        
        print('Creating the collage...')
        collage = Image.new('RGB', [prefs.size*IMAGE_SIZE]*2)

        for image, release, position in zip(images, releases, self._image_positions(prefs)):
            
            collage.paste(
                (Image.open(io.BytesIO(image)) if image 
                 else Image.new('RGB', [IMAGE_SIZE]*2, (0, 0, 0))),
                position,
            )

            if prefs.details: self._add_details(collage, release, position)

        return collage
            
    def _image_positions(self, prefs: Preferences) -> tuple[int, int]:
        ''' Yield the position each image should be in the collage in series '''

        x, y = 0, 0
        for row in range(prefs.size):
            for column in range(prefs.size):
                yield x, y
                x += IMAGE_SIZE
            y += IMAGE_SIZE
            x = 0

    def _pad_position(self, position: tuple[int, int], padding=0.025):
        ''' Adding padding to image positions for printing text details '''

        return tuple([pos+padding*IMAGE_SIZE for pos in position])

    def _add_details(self, image: Image, release: dict, position: tuple[int, int]):
        ''' Print the release details on the cover if requested '''

        draw = ImageDraw.Draw(image)
        draw.text(
            self._pad_position(position), 
            '{release_name}\n{artist_name}'.format(**release), 
            (255, 255, 255), 
            font=ImageFont.truetype('fonts/CascadiaCode-Bold.ttf', 10),
        )

    def save_collage(self, prefs: Preferences, collage: Image):
        ''' Save the collage to a file, stamped with some preferences and the date '''

        date_string = datetime.datetime.now().strftime('%d%b%Y')
        filename = f'lbcollage_{prefs.username}_{prefs.timespan}_{date_string}.jpg'
        collage.save(os.path.join(prefs.output, filename) if prefs.output else filename)
        print(f'Successfully saved as \'{filename}\'!')

