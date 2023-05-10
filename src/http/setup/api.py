from typing import Any, Callable

from fastapi import FastAPI

from .. import app_name, version_str
from ..config import Config
from ..handlers import setup_handlers


def setup_api(
    config: Config,
    dependency_overrides: dict[Callable[..., Any], Callable[..., Any]],
):
    app = FastAPI(debug=config.app.is_dev, title=app_name, version=version_str)
    app.dependency_overrides.update(dependency_overrides)
    setup_handlers(app)
    return app
