import argparse

class Preferences:
    ''' Manage user-specific settings based on command line arguments '''

    def __init__(self):

        parser = self._configure_parser()
        args = parser.parse_args()

        for arg, value in vars(args).items():
            setattr(self, arg, value)
        self.number = self.size**2

    def _configure_parser(self) -> argparse.ArgumentParser:
        ''' Set up argparse and provide the necessary info for a help page '''

        parser = argparse.ArgumentParser(
            prog='lbcollage',
            description='Create a collage of album art from your ListenBrainz listening history',
        )

        parser.add_argument(
            'username', 
            help='Your ListenBrainz username',
        )

        parser.add_argument(
            '-t', '--timespan', 
            metavar='timespan',
            help=('What timespan to consider - week, month, year, or all_time (default month)'),
            choices=['week', 'month', 'year', 'all_time'],
            default='month',
            type=str,
        )

        parser.add_argument(
            '-s', '--size', 
            metavar='size',
            help=('Choose what size the collage will be - the side length of the square'
                  '(default 3)'),
            default=3,
            type=int,
        )

        parser.add_argument(
            '-d', '--details', 
            #metavar='details',
            help='Print the album details on the covers',
            default=False,
            action='store_true',
        )

        parser.add_argument(
            '-o', '--output', 
            metavar='output',
            help='Set a custom output location for the collage image file',
            default=None,
            type=str,
        )

        return parser
