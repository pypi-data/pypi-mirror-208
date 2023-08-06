from unittest import TestCase

from bfs.config import Settings


class TestSettings(TestCase):
    def setUp(self):
        self.settings = Settings()

    def test_is_singleton(self):
        settings_duplicate = Settings()
        self.assertEqual(self.settings, settings_duplicate)

    def test_env_vars(self):
        self.assertIsNotNone(self.settings.dotenv_path)
        self.assertIsNotNone(self.settings.SECRET_KEY)
        self.assertIsNotNone(self.settings.DATABASE_ENGINE)
        self.assertIsNotNone(self.settings.DATABASE_NAME)
        self.assertIsNotNone(self.settings.DATABASE_USER)
        self.assertIsNotNone(self.settings.DATABASE_PASSWORD)
        self.assertIsNotNone(self.settings.DATABASE_HOST)
