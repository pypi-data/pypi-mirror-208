import os

SCUTILS_RESOURCE_DIR = os.path.join(os.path.dirname(__file__), 'resources')

from anutils.scutils import annotation as anno
from anutils.scutils import data, external
from anutils.scutils import plotting as pl
from anutils.scutils import preprocessing as pp
from anutils.scutils import utils
