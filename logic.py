from operator import itemgetter
from flask import Flask, render_template, request, url_for, redirect, flash, session
from datetime import datetime
import user_controller, data_manager_answers, data_manager_questions


def get_time():
    return str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def list_questions():
    order_by = request.args.get('order_by', 'submission_time')
    order_direction = request.args.get("order_direction", 'asc')
    user_questions = data_manager_questions.get_question_data()
    for question in user_questions:
        question['view_number'] = int(question['view_number'])
        question['vote_number'] = int(question['vote_number'])
    sorted_questions_by_recent = sorted(user_questions, key=itemgetter(order_by), reverse=order_direction == 'desc')

    return sorted_questions_by_recent, order_by, order_direction, user_questions

def display_question(question_id):
    increment_view_number = request.args.get('increment_view_number', False)
    if increment_view_number:
        data_manager_questions.count_visits(question_id)
    user_question = data_manager_questions.get_question_by_id(question_id)
    user_answers = data_manager_answers.get_answers_by_id(question_id)
    user_comments_to_questions = data_manager_questions.get_question_comments(question_id)
    for answer in user_answers:
        comments_to_answer = data_manager_answers.get_answers_comments(answer['id'])
        answer['comments'] = comments_to_answer

    return user_question, user_answers, user_comments_to_questions

def add_question():
    title = request.form.get('title')
    message = request.form.get('message')
    user_id = session['id']
    id = data_manager_questions.add_question(title, message, user_id)
    user_controller.increase_number_of_questions(user_id)

    return id

def add_answer(question_id):
    message = request.form.get('message')
    user_id = session['id']
    data_manager_answers.write_answer(question_id, message, user_id)
    user_controller.increase_number_of_answers(user_id)

def add_comment_to_question(question_id):
    comment = request.form.get("message")
    user_id = session['id']
    data_manager_questions.write_comment(question_id, comment, user_id)
    user_controller.increase_number_of_comments(user_id)

def edit_question(question_id):
    title = request.form.get('title')
    message = request.form.get('message')
    data_manager_questions.edit_question(title, message, question_id)

def edit_answer(answer_id):
    message = request.form.get('message')
    data_manager_answers.edit_answer(message, answer_id)

def edit_question_comment(comment_id):
    message = request.form.get('message')
    data_manager_questions.edit_question_comment(message, comment_id)

def edit_answer_comment(comment_id):
    message = request.form.get('message')
    data_manager_questions.edit_question_comment(message, comment_id)

def question_vote_up(question_id):
    user_id = session['id']
    data_manager_questions.vote_up_on_questions(question_id)
    user_controller.gain_reputation_questions(user_id)

def question_vote_down(question_id):
    user_id = session['id']
    data_manager_questions.vote_down_on_questions(question_id)
    user_controller.lose_reputation(user_id)

def answer_vote_up(answer_id):
    user_id = session['id']
    answer = data_manager_answers.get_answer(answer_id)
    data_manager_answers.vote_up_on_answer(answer_id)
    user_controller.gain_reputation_answers(user_id)

    return answer

def answer_vote_down(answer_id):
    user_id = session['id']
    answer = data_manager_answers.get_answer(answer_id)
    data_manager_answers.vote_down_on_answer(answer_id)
    user_controller.lose_reputation(user_id)

    return answer

def search():
    search_phrase = request.args.get('search_phrase')
    search_in_questions = data_manager_questions.get_search_result_questions(search_phrase)
    search_in_answers = data_manager_answers.get_search_result_answers(search_phrase)
    search_results = []
    list_of_id = []
    for element in search_in_answers + search_in_questions:
        if element['id'] not in list_of_id:
            list_of_id.append(element['id'])
            search_results.append(element)

    return search_results, search_phrase

def add_comment_to_answer(answer_id, question_id):
    answer_comment = request.form.get("message")
    user_id = session['id']
    data_manager_answers.add_comment_to_answer(question_id, answer_id, answer_comment, user_id)
    user_controller.increase_number_of_comments(user_id)

def user_details(user_id):
    current_user_data = user_controller.get_current_user_data(user_id)[0]
    current_user_questions = user_controller.get_current_user_questions(user_id)
    current_user_answers = user_controller.get_current_user_answers(user_id)
    current_user_comments = user_controller.get_current_user_comments(user_id)

    return current_user_data, current_user_questions, current_user_answers, current_user_comments

def accept_answer(answer_id):
    answer = data_manager_answers.get_one_answers_by_id(answer_id)
    user_controller.change_accepted_state(answer_id)

    if answer['accepted'] == True:
        user_controller.loose_reputation_acceptance(answer['user_id'])
    else:
        user_controller.gain_reputation_acceptance(answer['user_id'])