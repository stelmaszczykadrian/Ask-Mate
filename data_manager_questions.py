import database_common
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import util

@database_common.connection_handler
def get_question_data(cursor):
    query = """ SELECT * 
                FROM question 
                ORDER BY id"""

    cursor.execute(query)
    return cursor.fetchall()

@database_common.connection_handler
def get_latest_questions(cursor):
    query = """ SELECT id,submission_time,view_number,vote_number,title,message
                FROM question 
                ORDER BY submission_time DESC
                LIMIT 5"""

    cursor.execute(query)
    return cursor.fetchall()

@database_common.connection_handler
def get_question_comments(cursor,question_id):
    query = """ SELECT * 
                FROM comment 
                WHERE question_id=%(question_id)s
                AND answer_id is null
                ORDER BY id"""

    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_question_by_id(cursor, question_id):
    query = f""" SELECT * 
                FROM question 
                WHERE id = {question_id}
                ORDER BY id"""

    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def get_comment_by_id(cursor, comment_id):
    query = f""" SELECT * 
                FROM comment 
                WHERE id = %(comment_id)s
                ORDER BY id"""

    cursor.execute(query, {'comment_id': comment_id})
    return cursor.fetchone()

@database_common.connection_handler
def add_question(cursor, title, message,):
    submission_time = util.get_time()
    query = """
                INSERT INTO question
                VALUES (DEFAULT,%(submission_time)s, 0, 0, %(title)s, %(message)s, NULL)
                RETURNING id;
            """
    cursor.execute(query, {'submission_time': submission_time, 'title': title, 'message': message})
    return cursor.fetchone()

@database_common.connection_handler
def add_new_comment(cursor, question_id, message):
    submission_time = util.get_time()
    query = """
        INSERT INTO comment(question_id, message, submission_time, edited_count)
        VALUES (%(question_id)s, %(message)s, %(submission_time)s, 0)
        """
    cursor.execute(query, {"question_id": question_id, "message": message, "submission_time": submission_time})

@database_common.connection_handler
def edit_question(cursor, title, message, question_id):
    query = f"""
                UPDATE question
                SET title = %(title)s,
                    message = %(message)s
                WHERE id = {question_id}
            
            """
    cursor.execute(query, {'title': title, 'message': message, 'id': question_id})


@database_common.connection_handler
def edit_question_comment(cursor, message, comment_id):
    submission_time = util.get_time()
    query = """
                UPDATE comment
                SET message = %(message)s,
                    submission_time = %(submission_time)s,
                    edited_count = edited_count + 1 
                WHERE id = %(comment_id)s

            """
    cursor.execute(query, {'message': message, 'comment_id': comment_id, 'submission_time': submission_time})

@database_common.connection_handler
def delete_question(cursor, question_id):
    query = """
                DELETE FROM question_tag
                WHERE question_id = %(question_id)s;
                DELETE FROM comment
                WHERE question_id = %(question_id)s;
                DELETE FROM answer
                WHERE question_id=%(question_id)s;
                DELETE FROM question
                WHERE id=%(question_id)s
                
                """
    cursor.execute(query, {'question_id': question_id})



@database_common.connection_handler
def delete_comment(cursor, comment_id):
    query = """
                DELETE FROM comment
                WHERE id=%(comment_id)s
                """
    cursor.execute(query, {'comment_id': comment_id})


@database_common.connection_handler
def vote_up_on_questions(cursor, question_id):
    query = """
                    UPDATE question
                    SET vote_number = vote_number + 1
                    WHERE id=%(question_id)s

                """
    cursor.execute(query, {'question_id': question_id})


@database_common.connection_handler
def vote_down_on_questions(cursor, question_id):
    query = """
                    UPDATE question
                    SET vote_number = vote_number - 1
                    WHERE id=%(question_id)s

                """
    cursor.execute(query, {'question_id': question_id})


@database_common.connection_handler
def count_visits(cursor, id):
    query = """
                    UPDATE question
                    SET view_number = view_number + 1
                    WHERE id=%(id)s

                """
    cursor.execute(query, {'id': id})
@database_common.connection_handler
def get_search_result_questions(cursor, search_phrase):
    query = f""" SELECT * 
                FROM question
                WHERE title 
                LIKE '%{search_phrase}%' 
                OR message
                LIKE '%{search_phrase}%'
         
                """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_tags(cursor, question_id):
    cursor.execute("""
                    SELECT * FROM tag
                    JOIN question_tag
                    ON tag.id = question_tag.tag_id
                    WHERE question_id = %(question_id)s""",
                   {'question_id': question_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_all_tags(cursor):
    cursor.execute("""SELECT * FROM tag""")
    return cursor.fetchall()


@database_common.connection_handler
def get_tag_id(cursor, tag: str):
    cursor.execute("""SELECT id FROM tag WHERE name LIKE %(tag)s""", {'tag': tag})
    return cursor.fetchall()[0]['id']


@database_common.connection_handler
def add_new_tag(cursor, new_tag: str, question_id):
    tags = [tag['name'] for tag in get_all_tags()]
    if new_tag not in tags:
        cursor.execute("""
                        INSERT INTO tag (name)
                        VALUES (%(new_tag)s)""",
                       {'new_tag': new_tag})
    tag_id = get_tag_id(new_tag)
    try:
        cursor.execute("""
                        INSERT INTO question_tag (question_id, tag_id)
                        VALUES (%(question_id)s, %(tag_id)s)
                        """,
                       {'question_id': question_id, 'tag_id': tag_id})
    except:
        pass

@database_common.connection_handler
def tag_delete_from_question(cursor, question_id, tag_id):
    cursor.execute("""
                    DELETE FROM question_tag
                    WHERE question_id = %(question_id)s
                    AND tag_id = %(tag_id)s
                    """,
                   {'question_id': question_id, 'tag_id': tag_id})