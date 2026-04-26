from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json


@dataclass
class TodoItem:
    id: int
    title: str
    done: bool = False


class TodoStore:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def _load(self) -> list[TodoItem]:
        if not self.file_path.exists():
            return []
        raw = json.loads(self.file_path.read_text(encoding="utf-8"))
        return [TodoItem(**item) for item in raw]

    def _save(self, items: list[TodoItem]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(item) for item in items]
        self.file_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def list_items(self) -> list[TodoItem]:
        return self._load()

    def add_item(self, title: str) -> TodoItem:
        items = self._load()
        next_id = max((item.id for item in items), default=0) + 1
        new_item = TodoItem(id=next_id, title=title)
        items.append(new_item)
        self._save(items)
        return new_item

    def mark_done(self, item_id: int) -> TodoItem:
        items = self._load()
        for item in items:
            if item.id == item_id:
                item.done = True
                self._save(items)
                return item
        raise ValueError(f"Item id={item_id} not found")

    def remove_item(self, item_id: int) -> TodoItem:
        items = self._load()
        for index, item in enumerate(items):
            if item.id == item_id:
                removed = items.pop(index)
                self._save(items)
                return removed
        raise ValueError(f"Item id={item_id} not found")
