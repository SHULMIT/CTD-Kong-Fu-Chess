"""
Application entry point.
"""

from app.desktop_application_factory import DesktopApplicationFactory


def main() -> None:

    application = DesktopApplicationFactory.create()

    application.run()


if __name__ == "__main__":
    main()
