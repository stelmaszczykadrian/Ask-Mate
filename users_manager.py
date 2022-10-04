import database_common


@database_common.connection_handler
def get_users_list(cursor):
    query = '''SELECT user_name, registration_date 
                FROM users 
                ORDER BY user_name'''
    cursor.execute(query)
    return cursor.fetchall()

