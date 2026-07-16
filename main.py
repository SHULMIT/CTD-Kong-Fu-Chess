"""
Application entry point.
"""

from app.game_factory import GameFactory


def main() -> None:

    application = GameFactory.create()

    application.run()


if __name__ == "__main__":
    main()