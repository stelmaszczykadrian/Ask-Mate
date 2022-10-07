import database_common

USER_HEADER = ['id', 'username', 'registration date', 'asked_questions', 'answers', 'comments', 'reputation']
@database_common.connection_handler
def get_current_user_id(cursor, email):
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
                    SELECT question.submission_time, question.view_number, question.vote_number, question.title, question.message, question.image
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

@database_common.connection_handler
def get_users_list(cursor):
    query = '''SELECT id, user_name, registration_date, number_of_asked_questions, number_of_answers, number_of_comments, reputation 
                FROM users 
                ORDER BY id'''
    cursor.execute(query)
    return cursor.fetchall()

@database_common.connection_handler
def increase_number_of_questions(cursor, user_id):
    query = """
        UPDATE users
        SET number_of_asked_questions = number_of_asked_questions + 1
        WHERE id = %(user_id)s;"""
    cursor.execute(query, {'user_id': user_id})

@database_common.connection_handler
def increase_number_of_answers(cursor, user_id):
    query = """
        UPDATE users
        SET number_of_answers = number_of_answers + 1
        WHERE id = %(user_id)s;"""
    cursor.execute(query, {'user_id': user_id})

@database_common.connection_handler
def increase_number_of_comments(cursor, user_id):
    query = """
        UPDATE users
        SET number_of_comments = number_of_comments+ 1
        WHERE id = %(user_id)s;"""
    cursor.execute(query, {'user_id': user_id})

@database_common.connection_handler
def gain_reputation_answers(cursor, user_id):
    query = """
             UPDATE users
             SET reputation = reputation + 5
             WHERE id = %(user_id)s;"""
    cursor.execute(query, {'user_id': user_id})


@database_common.connection_handler
def gain_reputation_questions(cursor, user_id):
    query = """
             UPDATE users
             SET reputation = reputation + 10
             WHERE id = %(user_id)s;"""
    cursor.execute(query, {'user_id': user_id})


@database_common.connection_handler
def lose_reputation(cursor, user_id):
    query = """
             UPDATE users
             SET reputation = reputation - 2
             WHERE id = %(user_id)s;"""
    cursor.execute(query, {'user_id': user_id})

@database_common.connection_handler
def change_accepted_state(cursor, answer_id):
    query = """
             UPDATE answer
             SET accepted = NOT accepted
             WHERE id = %s;"""
    cursor.execute(query, (answer_id, ))

@database_common.connection_handler
def gain_reputation_acceptance(cursor, user_id):
    query = """
             UPDATE users
             SET reputation = reputation + 15
             WHERE id = %(user_id)s"""
    cursor.execute(query, {'user_id': user_id})

@database_common.connection_handler
def loose_reputation_acceptance(cursor, user_id):
    query = """
             UPDATE users
             SET reputation = reputation - 15
             WHERE id = %(user_id)s"""
    cursor.execute(query, {'user_id': user_id})