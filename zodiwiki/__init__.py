from zodiwiki.app import app
import zodiwiki.routes
from zodiwiki.__data__ import __version__, __author__
try:
    from zodiwiki.secrets import __secret_key__
except ImportError:
    pass
else:
    app.secret_key = __secret_key__
    del __secret_key__
