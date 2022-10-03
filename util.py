from datetime import datetime

ANSWER_HEADER = ['submission_time', 'vote_number', 'question_id', 'message']
QUESTION_HEADER = ['title', 'message','view number', 'title' , 'message']

def get_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')