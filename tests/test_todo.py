from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from todo_mvp.cli import main
from todo_mvp.todo import TodoStore


class TodoStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "todos.json"
        self.store = TodoStore(self.db_path)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_add_and_list(self) -> None:
        self.store.add_item("write tests")
        items = self.store.list_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id, 1)
        self.assertEqual(items[0].title, "write tests")
        self.assertFalse(items[0].done)

    def test_mark_done(self) -> None:
        item = self.store.add_item("finish MVP")
        updated = self.store.mark_done(item.id)
        self.assertTrue(updated.done)

    def test_remove(self) -> None:
        item = self.store.add_item("remove me")
        removed = self.store.remove_item(item.id)
        self.assertEqual(removed.id, item.id)
        self.assertEqual(self.store.list_items(), [])


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "todos.json"

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def run_cli(self, *args: str) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = main([*args])
        return code, output.getvalue()

    def test_cli_happy_path(self) -> None:
        from todo_mvp import cli

        original_resolve = cli.resolve_db_path
        cli.resolve_db_path = lambda: self.db_path
        try:
            code, _ = self.run_cli("add", "task one")
            self.assertEqual(code, 0)

            code, listed = self.run_cli("list")
            self.assertEqual(code, 0)
            self.assertIn("task one", listed)

            code, _ = self.run_cli("done", "1")
            self.assertEqual(code, 0)

            code, listed = self.run_cli("list")
            self.assertIn("[x] 1: task one", listed)
        finally:
            cli.resolve_db_path = original_resolve

    def test_cli_not_found(self) -> None:
        from todo_mvp import cli

        original_resolve = cli.resolve_db_path
        cli.resolve_db_path = lambda: self.db_path
        try:
            code, output = self.run_cli("done", "999")
            self.assertEqual(code, 1)
            self.assertIn("not found", output)
        finally:
            cli.resolve_db_path = original_resolve


if __name__ == "__main__":
    unittest.main()
