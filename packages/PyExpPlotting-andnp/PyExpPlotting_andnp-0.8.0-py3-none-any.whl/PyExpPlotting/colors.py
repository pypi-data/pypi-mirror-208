from typing import Dict

class ColorPalette:
    def __init__(self):
        self._mapper: Dict[str, str] = {}
        self._idx = 0

    def get(self, label: str | None):
        if label is None:
            label = ''

        if label not in self._mapper:
            self._mapper[label] = self.next()

        return self._mapper[label]

    def lock(self, colors: Dict[str, str]):
        self._mapper |= colors
        return self

    def next(self):
        self._idx += 1
        return ''
