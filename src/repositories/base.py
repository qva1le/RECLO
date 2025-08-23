from src.repositories.mappers.base import DataMapper


class BaseRepository:

    model = None
    schema: DataMapper = None

    def __init__(self, session, mapper):
        self.session = session
        self.mapper = mapper


