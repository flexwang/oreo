"""Oreo — your floating desktop cat companion."""

import argparse
import sys
from PyQt6.QtWidgets import QApplication
from pet_widget import PetWidget


def main():
    parser = argparse.ArgumentParser(description="Oreo — floating desktop cat.")
    parser.add_argument("--meow", action="store_true", help="Play meow sound when Oreo stretches.")
    args, qt_args = parser.parse_known_args()

    app = QApplication([sys.argv[0], *qt_args])
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("Oreo")

    pet = PetWidget(sound_enabled=args.meow)
    pet.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
