from unittest import TestCase

from bfs.database import AbstractDataBase


class TestDataBase(AbstractDataBase):
    def init_db(self):
        self.Base.metadata.create_all(bind=self.engine)


class TestAbstractDataBase(TestCase):
    def setUp(self):
        self.test_data_base = TestDataBase()

    def test_engine(self):
        self.assertIsNotNone(self.test_data_base.engine)

    def test_db_session(self):
        self.assertIsNotNone(self.test_data_base.db_session)
        self.assertEqual(self.test_data_base.db_session.bind, self.test_data_base.engine)
