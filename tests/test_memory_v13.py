"""Tests for termucoder.memory v1.3 — TF-IDF, dedup, tags, export/import."""
import json
import os
import tempfile
import unittest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestTFIDF(unittest.TestCase):

    def test_tokenize(self):
        from termucoder.memory import _tokenize
        result = _tokenize("Hello World 123")
        self.assertEqual(result, ["hello", "world", "123"])

    def test_tokenize_cyrillic(self):
        from termucoder.memory import _tokenize
        result = _tokenize("Привет мир")
        self.assertEqual(result, ["привет", "мир"])

    def test_idf_basic(self):
        from termucoder.memory import _compute_idf
        docs = ["hello world", "hello python", "world python"]
        idf = _compute_idf(docs)
        self.assertIn("hello", idf)
        self.assertIn("world", idf)
        self.assertIn("python", idf)

    def test_tfidf_score(self):
        from termucoder.memory import _tfidf_score, _compute_idf
        docs = ["hello world", "hello python", "world python"]
        idf = _compute_idf(docs)
        score = _tfidf_score(["hello"], ["hello", "world"], idf)
        self.assertGreater(score, 0)

    def test_search_returns_ranked(self):
        from termucoder.memory import search, add, delete, _ensure_dir, MEMORY_DIR
        _ensure_dir()
        e1 = add("API использует REST v2", tags=["api"])
        e2 = add("База данных PostgreSQL", tags=["db"])
        e3 = add("REST API для авторизации", tags=["api", "auth"])
        try:
            results = search("API")
            self.assertGreater(len(results), 0)
            self.assertEqual(results[0]["id"], e1["id"])
        finally:
            delete(e1["id"])
            delete(e2["id"])
            delete(e3["id"])


class TestFindSimilar(unittest.TestCase):

    def test_find_similar(self):
        from termucoder.memory import find_similar, add, delete, _ensure_dir
        _ensure_dir()
        e = add("API использует REST v2", tags=["api"])
        try:
            result = find_similar("API использует REST v2", threshold=0.5)
            self.assertIsNotNone(result)
            self.assertEqual(result["id"], e["id"])
        finally:
            delete(e["id"])

    def test_find_similar_no_match(self):
        from termucoder.memory import find_similar, add, delete, _ensure_dir
        _ensure_dir()
        e = add("База данных PostgreSQL", tags=["db"])
        try:
            result = find_similar("frontend react")
            self.assertIsNone(result)
        finally:
            delete(e["id"])


class TestGetAllTags(unittest.TestCase):

    def test_get_all_tags(self):
        from termucoder.memory import get_all_tags, add, delete, _ensure_dir
        _ensure_dir()
        e1 = add("test1", tags=["api", "rest"])
        e2 = add("test2", tags=["api", "db"])
        try:
            tags = get_all_tags()
            self.assertIn("api", tags)
            self.assertEqual(tags["api"], 2)
            self.assertIn("rest", tags)
            self.assertEqual(tags["rest"], 1)
        finally:
            delete(e1["id"])
            delete(e2["id"])


class TestExportImport(unittest.TestCase):

    def test_export_import(self):
        from termucoder.memory import export_all, import_all, add, delete, list_all, _ensure_dir
        _ensure_dir()
        e = add("export test data", tags=["export"])
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                tmp_path = f.name
            try:
                n = export_all(tmp_path)
                self.assertGreater(n, 0)
                with open(tmp_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.assertIsInstance(data, list)
                self.assertTrue(any(x["id"] == e["id"] for x in data))
            finally:
                os.unlink(tmp_path)
        finally:
            delete(e["id"])

    def test_import_no_duplicates(self):
        from termucoder.memory import import_all, add, delete, list_all, _ensure_dir
        _ensure_dir()
        e = add("import test", tags=["import"])
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump([e], f)
                tmp_path = f.name
            try:
                n = import_all(tmp_path)
                self.assertEqual(n, 0)
            finally:
                os.unlink(tmp_path)
        finally:
            delete(e["id"])


if __name__ == "__main__":
    unittest.main()
