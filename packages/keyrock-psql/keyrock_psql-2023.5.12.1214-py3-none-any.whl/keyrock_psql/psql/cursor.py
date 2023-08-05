import psycopg2.extras
import psycopg2.extensions

from collections import OrderedDict

### Preserves result column order
class OrderedDictCursor(psycopg2.extensions.cursor):
    def _to_od(self, tup):
        return OrderedDict((k[0], v) for k, v in zip(self.description, tup))

    def fetchone(self):
        t = super().fetchone()
        if t is not None:
            return self._to_od(t)

    def fetchmany(self, size=None):
        ts = super().fetchmany(size)
        return list(map(self._to_od, ts))

    def fetchall(self):
        ts = super().fetchall()
        return list(map(self._to_od, ts))

    def __iter__(self):
        it = super().__iter__()
        t = next(it)
        yield self._to_od(t)
        while 1:
            yield self._to_od(next(it))