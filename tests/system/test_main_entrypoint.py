"""System tests for the interactive application entry point."""

from unittest.mock import MagicMock, patch

import main


def test_main_creates_and_runs_the_game_application():
    application = MagicMock()

    with patch(
        "main.DesktopApplicationFactory.create",
        return_value=application,
    ) as create:
        main.main()

    create.assert_called_once_with()
    application.run.assert_called_once_with()
