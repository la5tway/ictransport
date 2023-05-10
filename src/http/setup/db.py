from src.infra.db.factories import create_engine, create_session_maker

from ..config import Config


def setup_db(config: Config):
    engine = create_engine(url=config.db.url, echo=False)
    session_maker = create_session_maker(engine)
    return engine, session_maker
