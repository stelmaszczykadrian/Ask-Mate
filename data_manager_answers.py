import database_common
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

import util

@database_common.connection_handler
def get_question_id_by_answer_id(cursor, answer_id):
    query = f"""
                SELECT question_id
                FROM answer
                WHERE id = {answer_id}
            """
    cursor.execute(query)
    return cursor.fetchone()
@database_common.connection_handler
def get_answers_to_question(cursor):
    query = """ SELECT * 
                FROM answer 
                ORDER BY id"""

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_answers_by_id(cursor, id):
    query = f"""
                SELECT *
                FROM answer
                WHERE question_id = {id}
                """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_answer(cursor, id):
    query = f"""
                    SELECT *
                    FROM answer
                    WHERE id = %(id)s
                    """
    cursor.execute(query, {'id': id})
    return cursor.fetchone()

@database_common.connection_handler
def write_answer(cursor, question_id, message, user_id):
    submission_time = util.get_time()
    vote_number = 0
    image = ''
    query = """
    INSERT INTO answer (submission_time, vote_number, question_id, message, image, user_id) 
    VALUES (%s, %s, %s, %s, %s, %s);"""
    cursor.execute(query, (submission_time, vote_number, question_id, message, image, user_id))

@database_common.connection_handler
def edit_answer(cursor, message, id):
    query = """
                UPDATE answer
                SET message = %(message)s                 
                WHERE id=%(id)s
            """
    cursor.execute(query, {'message': message, 'id': id})


@database_common.connection_handler
def delete_answer(cursor, answer_id):
    query = """ 
                DELETE FROM comment
                WHERE answer_id = %(answer_id)s;
                DELETE FROM answer
                WHERE id=%(answer_id)s
                """
    cursor.execute(query, {'answer_id': answer_id})


@database_common.connection_handler
def vote_up_on_answer(cursor, answer_id):
    query = """
                    UPDATE answer
                    SET vote_number = vote_number + 1
                    WHERE id=%(answer_id)s

                """
    cursor.execute(query, {'answer_id': answer_id})


@database_common.connection_handler
def vote_down_on_answer(cursor, answer_id):
    query = """
                    UPDATE answer
                    SET vote_number = vote_number - 1
                    WHERE id=%(answer_id)s

                """
    cursor.execute(query, {'answer_id': answer_id})

@database_common.connection_handler
def get_search_result_answers(cursor, search_phrase):
    query = f""" SELECT * 
                FROM question
                WHERE id IN (SELECT question_id FROM answer WHERE message LIKE '%{search_phrase}%')                       
                """
    cursor.execute(query)
    return cursor.fetchall()

# @database_common.connection_handler
# def add_comment_to_answer(cursor, message, answer_id, question_id):
#     submission_time = util.get_time()
#     query = '''INSERT INTO  comment (answer_id, message, submission_time,question_id,edited_count)
#     VALUES (%(answer_id)s,%(message)s,  %(submission_time)s, %(question_id)s, 0)'''
#     cursor.execute(query, {"answer_id": answer_id,"message": message,  "submission_time": submission_time, "question_id" : question_id})

@database_common.connection_handler
def write_comment_to_answer(cursor, answer_id, message, user_id):
    submission_time = util.get_time()
    edited_count = 0
    query = """
    INSERT INTO comment (answer_id, message, submission_time, edited_count, user_id) 
    VALUES (%s, %s, %s, %s, %s);"""
    cursor.execute(query, (answer_id, message, submission_time,edited_count, user_id))
@database_common.connection_handler
def get_answers_comments(cursor, answer_id):
    query = """ SELECT * 
                    FROM comment 
                    WHERE answer_id=%(answer_id)s
                    ORDER BY id"""

    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchall()

@database_common.connection_handler
def add_comment_to_answer(cursor, question_id, answer_id, message, user_id):
    submission_time = util.get_time()

    query = f"""
                    INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count, user_id)
                    VALUES ({question_id}, {answer_id}, '{message}', '{submission_time}', 0, '{user_id}') 

            """
    cursor.execute(query)
@database_common.connection_handler
def get_comment_data(cursor):
    query = """
                SELECT *
                FROM comment
                ORDER BY id
            """
    cursor.execute(query)
    return cursor.fetchall()

# @database_common.connection_handler
# def edit_answer_comment(cursor, message, answer_id):
#     submission_time = util.get_time()
#     query = """
#                 UPDATE comment
#                 SET message = %(message)s,
#                 submission_time = %(submission_time)s
#                 WHERE id = %(answer_id)s
#             """
#     cursor.execute(query, {'message': message, 'answer_id': answer_id, 'submission_time': submission_time})