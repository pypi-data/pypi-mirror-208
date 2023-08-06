from unittest import TestCase

from utils.Table import Table, TableRow

TEST_DICT_LIST = [
    dict(name='Alice', age=30),
    dict(name='Bob', age=40),
    dict(name='Charlie', age=23),
    dict(name='Dinah', age=19),
]
TEST_TABLE = Table(TEST_DICT_LIST)
TEST_ROW = TableRow(TEST_DICT_LIST[0])


class TestTable(TestCase):
    # TableRow
    def test_row_to_dict(self):
        self.assertEqual(TEST_ROW.to_dict(), TEST_DICT_LIST[0])

    def test_row_eq(self):
        self.assertEqual(TEST_ROW, TableRow(TEST_DICT_LIST[0]))

        self.assertNotEqual(TEST_ROW, "TableRow")

    def test_row_fields(self):
        self.assertEqual(TEST_ROW.fields, ['name', 'age'])

    def test_row_getattr(self):
        self.assertEqual(TEST_ROW.name, TEST_DICT_LIST[0]['name'])

    def test_from_dict(self):
        self.assertEqual(TableRow.from_dict(TEST_DICT_LIST[0]), TEST_ROW)

    # Table
    def test_init(self):
        self.assertEqual(Table(TEST_DICT_LIST).to_dict_list(), TEST_DICT_LIST)
        self.assertEqual(TEST_TABLE.to_dict_list(), TEST_DICT_LIST)
        self.assertEqual(
            Table.from_dict(TEST_DICT_LIST).to_dict_list(), TEST_DICT_LIST
        )

    def test_len(self):
        self.assertEqual(len(TEST_TABLE), 4)

    def test_filter(self):
        self.assertEqual(
            TEST_TABLE.filter(lambda d: d['age'] > 30),
            Table([dict(name='Bob', age=40)]),
        )

    def test_fields(self):
        self.assertEqual(TEST_TABLE.fields, ['name', 'age'])

    def test_getitem(self):
        self.assertEqual(TEST_TABLE[0], TableRow(TEST_DICT_LIST[0]))

    def test_add(self):
        self.assertEqual(
            Table(TEST_DICT_LIST[:2]) + Table(TEST_DICT_LIST[2:4]),
            TEST_TABLE,
        )

    def test_map(self):
        self.assertEqual(
            TEST_TABLE.map(lambda d: dict(name=d['name'])),
            Table(
                [
                    {'name': 'Alice'},
                    {'name': 'Bob'},
                    {'name': 'Charlie'},
                    {'name': 'Dinah'},
                ]
            ),
        )

    def test_eq(self):
        self.assertEqual(TEST_TABLE, Table(TEST_DICT_LIST))
        self.assertNotEqual(TEST_TABLE, "Table")
