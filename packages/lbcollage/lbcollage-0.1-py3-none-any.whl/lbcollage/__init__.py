from .preferences import Preferences
from .brainzrequest import BrainzRequest
from .imageprocessing import ImageProcessing

def main():

    IMAGE_SIZE = 250

    # Configure user preferences
    prefs = Preferences()

    # Request the necessary data from ListenBrainz and MusicBrainz
    brainz_request = BrainzRequest(prefs)

    # Compile the album art into a collage
    image_processing = ImageProcessing()
    collage = image_processing.create_collage(
        prefs, 
        brainz_request.cover_images, 
        brainz_request.releases,
    )

    # Save the collage to a local file
    image_processing.save_collage(prefs, collage)

