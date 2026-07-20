"""Тесты для termucoder.plugins (v0.7)."""

import os
import tempfile
import unittest

from termucoder.plugins import PluginRegistry
from termucoder.plugins.loader import _find_plugins, load_plugins
from termucoder.config import set_value, get_value


class TestPluginRegistry(unittest.TestCase):

    def test_add_command(self):
        reg = PluginRegistry()
        handler = lambda args: "ok"
        reg.add_command("greet", handler, "Поприветствовать")
        self.assertIn("greet", reg.commands)
        self.assertEqual(reg.commands["greet"]["handler"], handler)
        self.assertEqual(reg.commands["greet"]["help"], "Поприветствовать")

    def test_add_prompt(self):
        reg = PluginRegistry()
        reg.add_prompt("review", "Проведи код-ревью")
        self.assertEqual(reg.get_prompt("review"), "Проведи код-ревью")
        self.assertIsNone(reg.get_prompt("nonexistent"))

    def test_add_hook(self):
        reg = PluginRegistry()
        results = []
        reg.add_hook("before_ask", lambda **kw: results.append(kw.get("messages")))
        reg.run_hooks("before_ask", messages=["test"])
        self.assertEqual(results, [["test"]])

    def test_add_config_defaults(self):
        reg = PluginRegistry()
        reg.add_config_defaults("myplugin", {"enabled": True})
        self.assertEqual(reg.config_defaults["myplugin"], {"enabled": True})

    def test_run_hooks_error_silenced(self):
        reg = PluginRegistry()
        reg.add_hook("before_ask", lambda: 1/0)
        reg.run_hooks("before_ask")
        self.assertTrue(True)


class TestPluginLoader(unittest.TestCase):

    def setUp(self):
        self._orig = os.getcwd()
        self._tmp = tempfile.mkdtemp()
        os.chdir(self._tmp)

    def tearDown(self):
        os.chdir(self._orig)

    def _make_plugin(self, name, code='def register(r): pass'):
        path = os.path.join(".termucoder", "plugins", name)
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, "__init__.py"), "w") as f:
            f.write(code)

    def test_find_plugins_empty(self):
        plugins = _find_plugins(os.path.join(".termucoder", "plugins"))
        self.assertEqual(plugins, [])

    def test_find_plugins(self):
        self._make_plugin("my_plugin")
        plugins = _find_plugins(os.path.join(".termucoder", "plugins"))
        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0]["name"], "my_plugin")

    def test_find_plugins_with_meta(self):
        path = os.path.join(".termucoder", "plugins", "meta_plugin")
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, "__init__.py"), "w") as f:
            f.write("def register(r): pass")
        with open(os.path.join(path, "plugin.json"), "w") as f:
            f.write('{"name": "Meta", "version": "1.0", "description": "Test"}')
        plugins = _find_plugins(os.path.join(".termucoder", "plugins"))
        self.assertEqual(plugins[0]["name"], "Meta")
        self.assertEqual(plugins[0]["version"], "1.0")

    def test_load_plugins(self):
        self._make_plugin("test_plug", "def register(r): r.add_command('test', lambda a: 'ok')")
        reg = PluginRegistry()
        loaded = load_plugins(reg)
        self.assertEqual(len(loaded), 1)
        self.assertIn("test", reg.commands)

    def test_load_plugins_bad_code(self):
        self._make_plugin("bad_plug", "raise SyntaxError")
        reg = PluginRegistry()
        loaded = load_plugins(reg)
        self.assertEqual(loaded, [])

    def test_load_plugins_no_register(self):
        self._make_plugin("no_reg", "x = 1")
        reg = PluginRegistry()
        loaded = load_plugins(reg)
        self.assertEqual(loaded, [])


class TestConfigDeepKeys(unittest.TestCase):

    def setUp(self):
        self._orig = os.getcwd()
        self._tmp = tempfile.mkdtemp()
        os.chdir(self._tmp)

    def tearDown(self):
        os.chdir(self._orig)

    def test_set_deep_key(self):
        cfg = {"section": {}}
        set_value(cfg, "section.key.subkey", "value")
        self.assertEqual(cfg["section"]["key"]["subkey"], "value")

    def test_get_deep_key(self):
        cfg = {"a": {"b": {"c": 42}}}
        self.assertEqual(get_value(cfg, "a.b.c"), 42)
        self.assertIsNone(get_value(cfg, "a.b.d"))
        self.assertEqual(get_value(cfg, "a.b.d", "default"), "default")

    def test_set_value_two_levels_still_works(self):
        cfg = {}
        set_value(cfg, "server.port", "9090")
        self.assertEqual(cfg["server"]["port"], 9090)


if __name__ == "__main__":
    unittest.main()
