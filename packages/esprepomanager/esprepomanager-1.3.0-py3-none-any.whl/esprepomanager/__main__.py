"""Main entry point"""

import sys
if sys.argv[0].endswith("__main__.py"):
    sys.argv[0] = "python -m pyrepomanager"

from . import main
main()
