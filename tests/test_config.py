"""Тесты для termucoder.config."""

import os
import tempfile
import unittest

from termucoder import config


class TestConfig(unittest.TestCase):

    def setUp(self):
        self._orig = os.getcwd()
        self._tmp = tempfile.mkdtemp()
        os.chdir(self._tmp)

        # Убедимся, что settings.json отсутствует.
        if os.path.exists(config.CONFIG_FILE):
            os.remove(config.CONFIG_FILE)

    def tearDown(self):
        os.chdir(self._orig)

    def test_load_default_is_copy(self):
        a = config.load_config()
        b = config.load_config()
        self.assertIsNot(a, b)
        self.assertEqual(a["server"]["port"], 8080)

    def test_coerce(self):
        self.assertEqual(config._coerce("42"), 42)
        self.assertEqual(config._coerce("0.5"), 0.5)
        self.assertEqual(config._coerce("true"), True)
        self.assertEqual(config._coerce("false"), False)
        self.assertEqual(config._coerce("name"), "name")

    def test_set_and_get_value(self):
        cfg = config.load_config()
        config.set_value(cfg, "generation.temperature", "0.7")
        self.assertEqual(cfg["generation"]["temperature"], 0.7)

        config.set_value(cfg, "model.name", "test.gguf")
        self.assertEqual(
            config.get_value(cfg, "model.name"), "test.gguf"
        )

    def test_set_value_bad_key(self):
        cfg = config.load_config()
        with self.assertRaises(ValueError):
            config.set_value(cfg, "badkey", "x")

    def test_init_and_save(self):
        config.init_config()
        self.assertTrue(os.path.exists(config.CONFIG_FILE))
        # Повторный вызов не перезаписывает.
        config.init_config()
        self.assertTrue(os.path.exists(config.CONFIG_FILE))


if __name__ == "__main__":
    unittest.main()
