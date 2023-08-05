# Fixing paths
import os
import sys
from dotenv import load_dotenv
import inspect

src_dir = os.path.dirname(
    os.path.abspath(inspect.getsourcefile(lambda: 0))
)
sys.path.insert(0, src_dir)
load_dotenv(os.path.join(src_dir, ".env.shared"))

os.environ["SRCDIR"] = src_dir
os.environ["MODELDIR"] = os.path.join(
    os.environ["SRCDIR"], os.environ["MODELDIRREL"]
)
os.environ["LCEDIR"] = os.path.join(
    os.environ["SRCDIR"], os.environ["LCEDIRREL"]
)
os.environ["SYNTHDIR"] = os.path.join(
    os.environ["SRCDIR"], os.environ["SYNTHDIRREL"]
)

from .math import *
from .attitude import *
from .visualization import *
from .profiling import *
from .time import *
from .tle import *
from .lighting import *
from .station import *
from .coordinates import *
from .spaceobject import *
from .geodetic import *
from .orbit import *
from .constants import *
from .constraints import *
from .interp import *
from .background import *
from .sampling import *

try:
    from .ctools.synthetic.synth_rpo import run
except ModuleNotFoundError as e:
    pass  # TODO: Fix this install
