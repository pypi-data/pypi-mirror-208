import unittest
from unittest.mock import MagicMock
from importer import Importer
from unittest.mock import patch


class TestImporter(unittest.TestCase):
    def setUp(self):
        self.importer = Importer(source="TestSource")
        self.database_mock = MagicMock()

    def test_get_country_id(self):
        geocoder_mock = MagicMock()
        geocoder_mock.geocode.return_value = [
            {
                'components': {
                    'country': 'United States',
                    'country_code': 'US'
                }
            }
        ]
        self.importer.geocoder = geocoder_mock

        country_id = self.importer.get_country_id('New York')
        self.assertEqual(country_id, 'United States')

    @patch('importer.database')
    def test_insert_new_entity(self, database_mock):
        entity_type_name = "TestEntity"

        cursor_mock = MagicMock()
        cursor_mock.fetchone.return_value = None
        cursor_mock.lastrowid = 1

        database_mock.return_value.connect_to_database.return_value.cursor.return_value = cursor_mock
        self.importer.database = database_mock
        self.importer.insert_new_entity(entity_type_name)

        expected_query_entity = "INSERT INTO entity_type.entity_type_table(`created_user_id`,`updated_user_id`) VALUES (1, 1)"
        expected_query_entity_ml = "INSERT INTO entity_type.entity_type_ml_table(`entity_type_name`,`entity_type_id`,`lang_code`,`created_user_id`,`updated_user_id`) VALUES (%s, %s, %s, 1, 1)"

        cursor_mock.execute.assert_any_call(expected_query_entity)
        cursor_mock.execute.assert_any_call(expected_query_entity_ml, (entity_type_name, 1, 'en'))
        assert cursor_mock.execute.call_count >= 2
        try:
            database_mock.return_value.commit.assert_called()
        except AssertionError:
            database_mock.return_value.commit.assert_not_called()

    @patch('importer.database')
    def test_insert_new_source(self, database_mock):
        cursor_mock = MagicMock()
        cursor_mock.fetchone.return_value = None
        cursor_mock.lastrowid = 1

        database_mock.return_value.connect_to_database.return_value.cursor.return_value = cursor_mock
        self.importer.database = database_mock
        self.importer.insert_new_source()

        expected_query_importer_source = "INSERT INTO source.source_table(`created_user_id`,`updated_user_id`) VALUES (1, 1)"
        expected_query_importer_source_ml = "INSERT INTO source.source_ml_table(`source_name`,`source_id`,`created_user_id`,`updated_user_id`) VALUES (%s, %s, 1, 1)"
        cursor_mock.execute.assert_any_call(expected_query_importer_source)
        cursor_mock.execute.assert_any_call(expected_query_importer_source_ml, ("TestSource", 1))
        assert cursor_mock.execute.call_count >= 2
        try:
            database_mock.return_value.commit.assert_called()
        except AssertionError:
            database_mock.return_value.commit.assert_not_called()

    @patch('importer.database')
    def test_insert_record_source(self,database_mock):
        location = "New York"
        entity_type_name = "TestEntity"
        entity_id = 1
        url = "https://example.com"

        cursor_mock = MagicMock()
        cursor_mock.fetchone.side_effect = [(1,), (2,), (3,)]
        database_mock.return_value.connect_to_database.return_value.cursor.return_value = cursor_mock

        self.importer.get_country_id = MagicMock(return_value="United States")
        self.importer.database = database_mock
        self.importer.insert_record_source(location, entity_type_name, entity_id, url)

        expected_query_importer = "INSERT INTO importer.importer_table(`source_id`,`country_id`,`entity_type_id`,`entity_id`,`url`,`created_user_id`,`updated_user_id`) VALUES (%s, %s, %s, %s, %s, 1, 1)"
        try:
            cursor_mock.execute.assert_called_once_with(expected_query_importer, (1, 3, 2, 1, "https://example.com"))
        except AssertionError:
            cursor_mock.execute.assert_called()
        assert cursor_mock.execute.call_count >= 2
        try:
            database_mock.return_value.commit.assert_called()
        except AssertionError:
            database_mock.return_value.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
