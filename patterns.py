#!/usr/bin/env python
"""Single contstant that stores information needed when parsing.

Describes regex's and other necessary data for passing different image boards.

"""

PATTERNS = {'4chan': {'base': r'(\w*://[\w.]*/\w*/)',
                      'filename': r'[\w.]*$',
                      'source': 'src/',
                      'thumb': 'thumb/',
                      'thumb_replace': ('.', 's.')},

            '888chan': {'base': r'(\w*://[\w.]*/\w*/)',
                        'filename': r'[\w.]*$',
                        'source': 'src/',
                        'thumb': 'thumb/',
                        'thumb_replace': ('.', 's.')},
            }