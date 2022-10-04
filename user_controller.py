import database_common
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

@database_common.connection_handler
def get_current_user_id(cursor,email):
    cursor.execute(f"""
                    SELECT id
                    FROM users
                    WHERE username = '{email}'
                    """)
    return cursor.fetchall()

@database_common.connection_handler
def get_current_user_data(cursor, user_id):
    cursor.execute(f"""
                    SELECT *, 
                    (SELECT count(*) FROM question WHERE user_id = users.id) AS number_of_asked_questions,
                    (SELECT count(*) FROM answer WHERE user_id = users.id) AS number_of_answers,
                    (SELECT count(*) FROM comment WHERE user_id = users.id) AS number_of_comments
                    FROM users
                    WHERE id = '{user_id}'
                    """)
    return cursor.fetchall()

@database_common.connection_handler
def get_current_user_questions(cursor,user_id):
    cursor.execute(f"""
                    SELECT *
                    FROM question
                    LEFT JOIN users
                    ON question.user_id=users.id
                    WHERE question.user_id = {user_id}
                    """);
    return cursor.fetchall()

@database_common.connection_handler
def get_current_user_answers(cursor, user_id):
    cursor.execute(f"""
                    SELECT answer.submission_time, answer.vote_number, answer.message, answer.image
                    FROM answer
                    LEFT JOIN users
                    ON answer.user_id=users.id
                    WHERE answer.user_id = {user_id}
                    """);
    return cursor.fetchall()

@database_common.connection_handler
def get_current_user_comments(cursor, user_id):
    cursor.execute(f"""
                    SELECT comment.submission_time, comment.message, comment.edited_count
                    FROM comment
                    LEFT JOIN users
                    ON comment.user_id=users.id
                    WHERE comment.user_id = {user_id}
                    """);
    return cursor.fetchall()