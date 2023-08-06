from circles_local_database_python.database import database
from opencage.geocoder import OpenCageGeocode
import os
from dotenv import load_dotenv
from CirclesLocalLoggerPython.LoggerServiceSingleton import locallgr
from functools import wraps
load_dotenv()


def log_function_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_message = "Function %s started." % func.__name__
        locallgr.log(start_message)

        result = func(*args, **kwargs)  # Execute the function

        finish_message = "Function %s completed." % func.__name__
        locallgr.log(finish_message)
        return result
    return wrapper


class Importer:
    def __init__(self, source):
        self.source_name = source

    def get_logger_message(self, current_function_name):
        start_message = "Function %s started." % current_function_name
        finish_message = "Function '%s' completed." % current_function_name
        return start_message, finish_message

    @log_function_execution
    def get_country_name(self, location):
        # Create a geocoder instance
        # current_function_name = inspect.currentframe().f_code.co_name
        # message = self.get_logger_message(current_function_name)[0]
        api_key = os.getenv("RDS_OPENCAGE_KEY")

        # Define the city or state
        geocoder = OpenCageGeocode(api_key)

        # Use geocoding to get the location details
        results = geocoder.geocode(location)

        if results and len(results) > 0:
            first_result = results[0]
            components = first_result['components']

            # Extract the country from components
            country = components.get('country', '')
            if not country:
                # If country is not found, check for country_code as an alternative
                country = components.get('country_code', '')
            return country

        else:
            return None

    @log_function_execution
    def insert_new_entity(self, entity_type_name):
        database_conn = database()
        db = database_conn.connect_to_database()
        cursor = db.cursor()

        cursor.execute("SELECT entity_type_id FROM {} WHERE entity_type_name = '{}'".format('entity_type.entity_type_ml_table', entity_type_name))
        entity_type_id = cursor.fetchone()

        if not entity_type_id:
            query_entity = "INSERT INTO {}(`created_user_id`,`updated_user_id`)" \
                              " VALUES (1, 1)".format('entity_type.entity_type_table')
            cursor.execute(query_entity)
            db.commit()

            last_inserted_id = cursor.lastrowid
            query_entity_ml = "INSERT INTO {}(`entity_type_name`,`entity_type_id`,`lang_code`,`created_user_id`,`updated_user_id`)" \
                              " VALUES (%s, %s, %s, 1, 1)".format('entity_type.entity_type_ml_table')
            cursor.execute(query_entity_ml, (entity_type_name, last_inserted_id, 'en'))

            db.commit()
        else:
            print("Entity already exist")
        db.close()

    @log_function_execution
    def insert_new_source(self):
        database_conn = database()
        db = database_conn.connect_to_database()
        cursor = db.cursor()

        cursor.execute("SELECT source_id FROM {} WHERE source_name = '{}'".format('source.source_ml_table', self.source_name))
        source_id = cursor.fetchone()

        if not source_id:
            query_importer_source = "INSERT INTO {}(`created_user_id`,`updated_user_id`)" \
                              " VALUES (1, 1)".format('source.source_table')
            cursor.execute(query_importer_source)
            db.commit()

            last_inserted_id = cursor.lastrowid
            query_importer_source_ml = "INSERT INTO {}(`source_name`,`source_id`,`created_user_id`,`updated_user_id`)" \
                              " VALUES (%s, %s, 1, 1)".format('source.source_ml_table')
            cursor.execute(query_importer_source_ml, (self.source_name, last_inserted_id))

            db.commit()
        else:
            print("Source already exist")
        db.close()

    @log_function_execution
    def insert_record_source(self, location, entity_type_name, entity_id, url):
        database_conn = database()
        db = database_conn.connect_to_database()
        cursor = db.cursor()

        cursor.execute("SELECT source_id FROM {} WHERE source_name = '{}'".format('source.source_ml_table', self.source_name))
        source_id = cursor.fetchone()

        country_name = self.get_country_name(location)
        cursor.execute(
            "SELECT id FROM {} WHERE name = '{}'".format('location.country_table', country_name))
        country_id = cursor.fetchone()

        cursor.execute("SELECT entity_type_id FROM {} WHERE entity_type_name = '{}'".format('entity_type.entity_type_ml_table', entity_type_name))
        entity_type_id = cursor.fetchone()

        query_importer = "INSERT INTO {}(`source_id`,`country_id`,`entity_type_id`,`entity_id`,`url`,`created_user_id`,`updated_user_id`)" \
                          " VALUES (%s, %s, %s, %s, %s, 1, 1)".format('importer.importer_table')

        cursor.execute(query_importer, (source_id[0], country_id[0], entity_type_id[0], entity_id, url))

        db.commit()
        db.close()


if __name__ == "__main__":
    pass
    # imp = Importer("monster")
    # print(imp.get_country_name("new york"))
