"""Tests for termucoder.tools (v1.4)."""
import os
import tempfile
import unittest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestToolRegistry(unittest.TestCase):

    def test_create_default_registry(self):
        from termucoder.tools import create_default_registry
        r = create_default_registry()
        self.assertEqual(len(r.list_tools()), 5)

    def test_list_schemas(self):
        from termucoder.tools import create_default_registry
        r = create_default_registry()
        schemas = r.list_schemas()
        self.assertEqual(len(schemas), 5)
        self.assertIn("function", schemas[0])

    def test_summary(self):
        from termucoder.tools import create_default_registry
        r = create_default_registry()
        s = r.summary()
        self.assertIn("read_file", s)
        self.assertIn("write_file", s)

    def test_execute_unknown(self):
        from termucoder.tools import create_default_registry
        r = create_default_registry()
        result = r.execute("nonexistent")
        self.assertIn("не найден", result)


class TestReadFile(unittest.TestCase):

    def test_read_file(self):
        from termucoder.tools import create_default_registry
        r = create_default_registry()
        result = r.execute("read_file", path="VERSION")
        self.assertIn("1.4.0", result)

    def test_read_file_range(self):
        from termucoder.tools import create_default_registry
        r = create_default_registry()
        result = r.execute("read_file", path="VERSION", start_line=1, end_line=1)
        self.assertIn("1.4.0", result)

    def test_read_file_not_found(self):
        from termucoder.tools import create_default_registry
        r = create_default_registry()
        result = r.execute("read_file", path="nonexistent.txt")
        self.assertIn("не найден", result)


class TestWriteFile(unittest.TestCase):

    def test_write_file(self):
        from termucoder.tools import create_default_registry
        r = create_default_registry()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            tmp = f.name
        try:
            result = r.execute("write_file", path=tmp, content="hello world")
            self.assertIn("записан", result)
            with open(tmp) as f:
                self.assertEqual(f.read(), "hello world")
        finally:
            os.unlink(tmp)

    def test_write_creates_dirs(self):
        from termucoder.tools import create_default_registry
        r = create_default_registry()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "sub", "file.txt")
            result = r.execute("write_file", path=path, content="test")
            self.assertIn("записан", result)
            self.assertTrue(os.path.exists(path))


class TestSearchCode(unittest.TestCase):

    def test_search_code(self):
        from termucoder.tools import create_default_registry
        r = create_default_registry()
        result = r.execute("search_code", pattern="def ", include="*.py", path="termucoder/tools")
        self.assertIn("read_file", result)

    def test_search_no_results(self):
        from termucoder.tools import create_default_registry
        r = create_default_registry()
        result = r.execute("search_code", pattern="XYZNONEXISTENT", path="termucoder")
        self.assertIn("не найдено", result)


class TestRunCommand(unittest.TestCase):

    def test_run_command(self):
        from termucoder.tools import create_default_registry
        r = create_default_registry()
        result = r.execute("run_command", command="echo hello")
        self.assertIn("hello", result)

    def test_run_command_timeout(self):
        from termucoder.tools import create_default_registry
        r = create_default_registry()
        result = r.execute("run_command", command="sleep 10", timeout=1)
        self.assertIn("Таймаут", result)


class TestListFiles(unittest.TestCase):

    def test_list_files(self):
        from termucoder.tools import create_default_registry
        r = create_default_registry()
        result = r.execute("list_files", path="termucoder/tools")
        self.assertIn("read_file.py", result)
        self.assertIn("write_file.py", result)

    def test_list_files_pattern(self):
        from termucoder.tools import create_default_registry
        r = create_default_registry()
        result = r.execute("list_files", path="termucoder/tools", pattern="*.py")
        self.assertIn("read_file.py", result)
        # Directories are always shown


if __name__ == "__main__":
    unittest.main()
