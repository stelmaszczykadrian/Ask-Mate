from datetime import datetime

ANSWER_HEADER = ['submission_time', 'vote_number', 'question_id', 'message']
QUESTION_HEADER = ['title', 'message', 'view number', 'title', 'message']
USER_HEADER = ['username', 'registration date']

def get_time():
    return str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))