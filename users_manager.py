import database_common


@database_common.connection_handler
def get_users_list(cursor):
    query = '''SELECT login, registration_date 
                FROM users 
                ORDER BY id'''
    cursor.execute(query)
    return cursor.fetchall()

