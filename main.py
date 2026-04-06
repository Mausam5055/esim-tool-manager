from tool_manager.ui.cli import app
from tool_manager.ui.gui import main as gui_main
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "gui":
        gui_main()
    else:
        app()

