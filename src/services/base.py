from src.utils.db_namager import DBManager


class BaseService:
    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db
