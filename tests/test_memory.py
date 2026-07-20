"""Тесты для termucoder.memory (v0.6)."""

import os
import tempfile
import unittest

from termucoder import memory


class TestMemory(unittest.TestCase):

    def setUp(self):
        self._orig = os.getcwd()
        self._tmp = tempfile.mkdtemp()
        os.chdir(self._tmp)

    def tearDown(self):
        os.chdir(self._orig)

    def test_add_and_get(self):
        entry = memory.add("Тестовая заметка", tags=["test"])
        self.assertEqual(entry["content"], "Тестовая заметка")
        self.assertEqual(entry["tags"], ["test"])
        self.assertEqual(entry["source"], "manual")
        self.assertIn("id", entry)
        self.assertIn("created", entry)

        loaded = memory.get(entry["id"])
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["content"], "Тестовая заметка")

    def test_get_nonexistent(self):
        self.assertIsNone(memory.get("nonexistent-id"))

    def test_delete(self):
        entry = memory.add("Для удаления")
        self.assertTrue(memory.delete(entry["id"]))
        self.assertIsNone(memory.get(entry["id"]))
        self.assertFalse(memory.delete(entry["id"]))

    def test_list_all(self):
        memory.add("Запись 1")
        memory.add("Запись 2")
        memory.add("Запись 3")
        entries = memory.list_all()
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0]["content"], "Запись 1")
        self.assertEqual(entries[2]["content"], "Запись 3")

    def test_search(self):
        memory.add("Используем SQLAlchemy для ORM")
        memory.add("Flask — это веб-фреймворк")
        memory.add("SQLAlchemy упрощает работу с БД")

        results = memory.search("SQLAlchemy")
        self.assertEqual(len(results), 2)

        results = memory.search("Flask")
        self.assertEqual(len(results), 1)

        results = memory.search("Django")
        self.assertEqual(len(results), 0)

    def test_search_case_insensitive(self):
        memory.add("Python — лучший язык")
        results = memory.search("python")
        self.assertEqual(len(results), 1)

    def test_list_by_tag(self):
        memory.add("API endpoint", tags=["api", "rest"])
        memory.add("База данных", tags=["database"])
        memory.add("Ещё API", tags=["api"])

        api_entries = memory.list_by_tag("api")
        self.assertEqual(len(api_entries), 2)

        db_entries = memory.list_by_tag("database")
        self.assertEqual(len(db_entries), 1)

    def test_get_context(self):
        memory.add("Проект использует FastAPI", tags=["web"])
        memory.add("БД — PostgreSQL", tags=["database"])

        ctx = memory.get_context()
        self.assertIn("FastAPI", ctx)
        self.assertIn("PostgreSQL", ctx)
        self.assertIn("[manual]", ctx)

    def test_get_context_empty(self):
        ctx = memory.get_context()
        self.assertEqual(ctx, "")

    def test_get_context_limit(self):
        for i in range(15):
            memory.add(f"Запись {i}")

        ctx = memory.get_context(max_entries=5)
        self.assertIn("Запись 14", ctx)
        self.assertNotIn("Запись 0", ctx)

    def test_count(self):
        self.assertEqual(memory.count(), 0)
        memory.add("одна")
        memory.add("две")
        self.assertEqual(memory.count(), 2)

    def test_source_chat(self):
        entry = memory.add("Из чата", source="chat")
        self.assertEqual(entry["source"], "chat")


if __name__ == "__main__":
    unittest.main()
