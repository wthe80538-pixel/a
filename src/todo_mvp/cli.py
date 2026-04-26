from __future__ import annotations

import argparse
import os
from pathlib import Path

from .todo import TodoStore


DEFAULT_DB_PATH = Path.home() / ".todo_mvp" / "todos.json"


def resolve_db_path() -> Path:
    env_path = os.getenv("TODO_MVP_DB")
    if env_path:
        return Path(env_path)
    return DEFAULT_DB_PATH


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Todo MVP CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a todo item")
    add_parser.add_argument("title", help="Todo title")

    subparsers.add_parser("list", help="List todo items")

    done_parser = subparsers.add_parser("done", help="Mark a todo item as done")
    done_parser.add_argument("id", type=int, help="Todo id")

    remove_parser = subparsers.add_parser("remove", help="Remove a todo item")
    remove_parser.add_argument("id", type=int, help="Todo id")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = TodoStore(resolve_db_path())

    try:
        if args.command == "add":
            item = store.add_item(args.title)
            print(f"Added [{item.id}] {item.title}")
            return 0

        if args.command == "list":
            items = store.list_items()
            if not items:
                print("No todo items.")
                return 0
            for item in items:
                status = "x" if item.done else " "
                print(f"[{status}] {item.id}: {item.title}")
            return 0

        if args.command == "done":
            item = store.mark_done(args.id)
            print(f"Marked done [{item.id}] {item.title}")
            return 0

        if args.command == "remove":
            item = store.remove_item(args.id)
            print(f"Removed [{item.id}] {item.title}")
            return 0
    except ValueError as err:
        print(f"Error: {err}")
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
