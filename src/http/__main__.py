from src.config import AppConfig
from src.http.main import main_sync
from src.infra.config_loader import load_config


def main():
    app_settings = load_config(AppConfig, scope="APP")
    if app_settings.is_dev:
        from src.utils.reloader import FileReloader

        reloader = FileReloader(target=main_sync)
        reloader.start()
    else:
        main_sync()


if __name__ == "__main__":
    main()
