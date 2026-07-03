"""Oreo — your floating desktop cat companion."""

import sys
from PyQt6.QtWidgets import QApplication
from pet_widget import PetWidget


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("Oreo")

    pet = PetWidget()
    pet.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
