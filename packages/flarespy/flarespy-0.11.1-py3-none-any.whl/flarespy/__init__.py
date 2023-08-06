from pathlib import Path

from .version import __version__ as __version__

PACKAGEDIR = Path(__file__).parent.resolve()

from .flarespy import convert_gaia_dr2_to_dr3 as convert_gaia_dr2_to_dr3
from .flarespy import load_from_lightkurve as load_from_lightkurve
