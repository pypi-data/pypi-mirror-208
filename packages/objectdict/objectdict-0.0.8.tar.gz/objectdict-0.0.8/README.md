# 使用方法
```
import json
from unittest import TestCase

from objectdict import ObjectDict


class TestObjectDict(TestCase):

    def test_value(self):
        class SimpleObjectDict(ObjectDict):
            int_field: int = 1
            str_field = 'a'
            dict_field = {}
            int2_f: int
            _protect = 'protect'

            @classmethod
            def classmethod(cls):
                pass

            @property
            def proty(cls):
                return 'property'

            def asd(self):
                return 'asd'

        self.assertEqual(ObjectDict(), {})

        self.assertEqual(SimpleObjectDict().int_field, 1)
        self.assertEqual(SimpleObjectDict().str_field, 'a')
        self.assertEqual(SimpleObjectDict().dict_field, {})
        self.assertEqual(SimpleObjectDict(), SimpleObjectDict().from_json(json.dumps(SimpleObjectDict())))

```