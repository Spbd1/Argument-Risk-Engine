from __future__ import annotations
import json
from pathlib import Path

class Cell:
    def __init__(self, value): self.value = value

class Worksheet:
    def __init__(self):
        self.rows = []
        self.title = 'Sheet'
    def append(self, row): self.rows.append(list(row))
    def iter_rows(self, min_row=1, max_row=None, values_only=False):
        rows = self.rows[min_row-1:max_row]
        for row in rows:
            yield tuple(row) if values_only else tuple(Cell(v) for v in row)

class Workbook:
    def __init__(self): self.active = Worksheet()
    def save(self, path): Path(path).write_text(json.dumps({'rows': self.active.rows}))

def load_workbook(path):
    data = json.loads(Path(path).read_text())
    wb = Workbook(); wb.active.rows = data.get('rows', [])
    return wb
