"""Application composition entry point."""

from evopharm_retail_erp.presentation.ui.main_window import MainWindow

APPLICATION_WINDOW: type[MainWindow] = MainWindow
