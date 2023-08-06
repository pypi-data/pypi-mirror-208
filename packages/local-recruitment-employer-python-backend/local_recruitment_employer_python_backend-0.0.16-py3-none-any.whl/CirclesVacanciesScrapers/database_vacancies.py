from CirclesBertPython.bert import BertCircles
from circles_local_database_python.database import database
from CirclesImporter.importer import Importer
from CirclesLocalLoggerPython.LoggerServiceSingleton import locallgr
from functools import wraps


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


class DatabaseVacancies:
    def __init__(self):
        self.bert = BertCircles()

    @log_function_execution
    def add_generic_job_titles(self, list_of_jobs):
        # Get a cursor to interact with the database
        db = self.connect_to_db()
        cursor = db.cursor()

        # Create the MySQL query to insert the data
        for title in list_of_jobs:
            cursor.execute("SELECT id FROM {} WHERE job_name = '{}'".format('vacancy.job_title_ml_table', title))
            id_exist = cursor.fetchone()
            if not id_exist:
                query_job_title = "INSERT INTO {}(`created_user_id`,`updated_user_id`) VALUES (1,1)".format('vacancy.job_title_table')
                cursor.execute(query_job_title)

                cursor.execute("SELECT MAX(id) FROM {}".format('vacancy.job_title_table'))
                job_title_id = cursor.fetchone()
                job_title_id = job_title_id[0]

                query_job_title_ml = "INSERT INTO {} (`job_title_id`, `lang_code`, `job_name`, `created_user_id`, `updated_user_id`) VALUES (%s, 'en', %s, 1, 1)".format('vacancy.job_title_ml_table')
                cursor.execute(query_job_title_ml,  (job_title_id, title))
                # Commit the changes to the database
                db.commit()

                query_group_table = "INSERT INTO {} (`id`) VALUES (NULL)".format('group.group_table')
                cursor.execute(query_group_table)
                # Commit the changes to the database
                db.commit()

                cursor.execute("SELECT MAX(id) FROM {}".format('group.group_table'))
                group_id = cursor.fetchone()
                group_id = group_id[0]

                query_group = "INSERT INTO {} (`group_id`, `job_title_id`, `created_user_id`, `updated_user_id`) VALUES (%s, %s, 1, 1)".format('vacancy.group_job_title_table')
                cursor.execute(query_group, (group_id, job_title_id))
                # Commit the changes to the database
                db.commit()
        # Close the database connection
        db.close()

    @log_function_execution
    def connect_to_db(self):
        # Connect to the MySQL database
        database_conn = database()
        db = database_conn.connect_to_database()
        return db

    @log_function_execution
    def add_data_to_mysql_database(self, df, source, location):
        # Get a cursor to interact with the database vacancy
        db = self.connect_to_db()
        cursor = db.cursor()
        # Create a list of tuples from the DataFrame values
        vac_name = df['Job_Title'].tolist()
        company_name = df["Company"].tolist()
        urls = df["url"].tolist()
        i = -1
        # Create the MySQL query to insert the data
        for title in vac_name:
            i += 1
            query_vac = "INSERT INTO {}(`created_user_id`,`updated_user_id`) VALUES (1,1)".format('vacancy.vacancy_table')
            cursor.execute(query_vac)
            cursor.execute("SELECT MAX(id) FROM {}".format('vacancy.vacancy_table'))
            vac_id = cursor.fetchone()
            vac_id = vac_id[0]

            imp = Importer(source)
            imp.insert_record_source(location, "vacancies", vac_id, urls[i])


            query_vac_ml = "INSERT INTO {} (`vacancy_id`, `lang_code`, `vacancy_name`, `created_user_id`, `updated_user_id`) VALUES (%s, 'en', %s, 1, 1)".format('vacancy.vacancy_ml_table')
            cursor.execute(query_vac_ml, (vac_id, title))

            job_title_and_id = self.bert.classify('job_title_id', 'job_name', 'vacancy.job_title_ml_table',db,title)
            job_title_id = int(job_title_and_id[1])
            query_job_title_vac = "INSERT INTO {}(`job_title_id`,`vacancy_id`,`created_user_id`,`updated_user_id`) VALUES (%s, %s, 1, 1)".format('vacancy.job_title_vacancy_table')
            cursor.execute(query_job_title_vac, (job_title_id, vac_id))
            db.commit()

            cursor.execute(
                "SELECT profile_id FROM {} WHERE employer_name = %s".format('employer.employer_profile_profile_table'),
                (company_name[i],))
            profile = cursor.fetchone()
            # if profile does not exist in the DB
            if not profile:
                cursor.execute("SELECT MAX(id) FROM {}".format('profile.profile_table'))
                profile = cursor.fetchone()
                profile = profile[0]
                profile += 1
                query_profile = "INSERT INTO {}(`id`,`number`) VALUES (NULL, %s)".format('profile.profile_table')
                cursor.execute(query_profile, (profile,))
                db.commit()

                query_profile_profile = "INSERT INTO {}(`employer_profile_id`,`profile_id`,`employer_name`,`created_user_id`,`updated_user_id`) VALUES (%s, %s, %s, 1, 1)".format('employer.employer_profile_profile_table')
                cursor.execute(query_profile_profile, (profile, profile, company_name[i]))
                db.commit()
            cursor.execute(
                "SELECT id FROM {} WHERE employer_name = %s".format('employer.employer_profile_profile_table'),
                (company_name[i],))
            result2 = cursor.fetchone()
            emp_id = result2[0]
            query_vacancy_profile = "INSERT INTO {}(`employer_profile_id`,`vacancy_id`,`created_user_id`,`updated_user_id`) VALUES (%s, %s, 1, 1)".format('employer.employer_profile_vacancy_table')
            cursor.execute(query_vacancy_profile, (emp_id, vac_id))
            db.commit()

        # Close the database connection
        db.close()


if __name__ == '__main__':
    pass
