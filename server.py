from operator import itemgetter
from flask import Flask, render_template, request, url_for, redirect, flash, session
from bonus_questions import SAMPLE_QUESTIONS

from markupsafe import Markup
from datetime import datetime
import time
from werkzeug.security import generate_password_hash, check_password_hash

import user_controller
import data_manager_answers
import data_manager_questions
import util
from bonus_questions import SAMPLE_QUESTIONS

app = Flask(__name__)
app.secret_key = 'ghbdtn93vbh65bdctv407yfv'


def get_logged_user():
    if 'user_name' in session:
        return {'user_name': session['user_name'], 'id': session['id']}
    else:
        return None


@app.route("/login", methods=["POST", 'GET'])
def login():
    user = {}
    invalid_credentials = False
    if request.method == "POST":
        user_name = request.form['email']
        password = request.form['psw']
        user_data = data_manager_questions.get_user_password(user_name)
        if user_data and check_password_hash(user_data['password'], password):
            session['id'] = user_data['id']
            session['user_name'] = user_name
            return redirect(url_for('main'))
        else:
            invalid_credentials = True
            print("bad login")

    return render_template('login.html',  title="authorization", invalid_credentials=invalid_credentials)
 
 
@app.route("/registration", methods=["POST", 'GET'])
def registration():
    ts_epoch = (int(time.time()))
    new_user = {}
    if request.method == "POST":
        if len(request.form['email']) > 4 \
           and len(request.form['psw']) > 3:
            hash = generate_password_hash(request.form['psw'])
            new_user['user_name'] = request.form['email']
            new_user['password'] = hash
            new_user['registration_date'] = datetime.fromtimestamp(
                ts_epoch).strftime('%Y-%m-%d %H:%M:%S')
            data_manager_questions.addUser(new_user)
            if new_user:
                flash("You have successfully registered!", category="success")
                return redirect(url_for('login'))
            else:
                flash("Error adding to database.", category="error")
        else:
            flash("The form contains errors.", category="error")

    return render_template('registration.html',  title="register")
    
@app.route("/bonus-questions")
def bonus_question():
    return render_template('bonus_questions.html', questions=SAMPLE_QUESTIONS)


@app.route("/", methods=['GET'])
def main():
    user_questions = data_manager_questions.get_latest_questions()
    all_questions_data = data_manager_questions.get_question_data()
    #return render_template('main.html', headers=util.QUESTION_HEADER, stories=user_questions)
    if 'id' in session:
        return render_template('main.html', headers=util.QUESTION_HEADER, stories=user_questions, logged_user = get_logged_user())
    return render_template('main.html')


@app.route("/logout")
def logout():
    session.pop('id', None)
    session.pop('user_name', None)
    return redirect(url_for("login"))
 

@app.route('/list', methods=['GET'])
def route_list():
    order_by = request.args.get('order_by', 'submission_time')
    order_direction = request.args.get("order_direction", 'asc')
    user_questions = data_manager_questions.get_question_data()
    for question in user_questions:
        question['view_number'] = int(question['view_number'])
        question['vote_number'] = int(question['vote_number'])

    sorted_questions_by_recent = sorted(user_questions, key=itemgetter(order_by), reverse=order_direction == 'desc')
    print(sorted_questions_by_recent)
    return render_template('list.html', headers=util.QUESTION_HEADER,
                           stories=sorted_questions_by_recent,
                           order_by=order_by, order_direction=order_direction, questions=user_questions)


@app.route('/question/<int:question_id>', methods=['GET'])
def question(question_id):
    increment_view_number = request.args.get('increment_view_number', False)
    if increment_view_number:
        data_manager_questions.count_visits(question_id)
    user_question = data_manager_questions.get_question_by_id(question_id)
    user_answers = data_manager_answers.get_answers_by_id(question_id)
    user_comments_to_questions = data_manager_questions.get_question_comments(question_id)
    for answer in user_answers:
        comments_to_answer = data_manager_answers.get_answers_comments(answer['id'])
        answer['comments'] = comments_to_answer

    return render_template('question.html', question=user_question, answers=user_answers,
                           user_comments_to_questions=user_comments_to_questions, question_id=question_id,
                           tags=data_manager_questions.get_tags(question_id))


@app.route('/questions', methods=['GET'])
def all_questions():
    user_questions = data_manager_questions.get_latest_questions()
    all_questions_data = data_manager_questions.get_question_data()
    #return render_template('main.html', headers=util.QUESTION_HEADER, stories=user_questions)
    if 'id' in session:
        return render_template('questions.html', headers=util.QUESTION_HEADER, stories=user_questions, logged_user = get_logged_user())
    return render_template('questions.html')
    

@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        user_id = session['id']
        id = data_manager_questions.add_question(title, message, user_id)
        return redirect(url_for('question', question_id=id['id']))
    return render_template('add-question.html')


@app.route('/question/<int:question_id>/new-answer', methods=['GET', 'POST'])
def add_answer(question_id):
    if request.method == 'POST':
        message = request.form.get('message')
        user_id = session['id']
        data_manager_answers.write_answer(question_id, message, user_id)
        return redirect(url_for('question', question_id=question_id))
    return render_template('new-answer.html', question_id=question_id)


@app.route("/question/<int:question_id>/new-comment", methods=['GET', 'POST'])
def comment_to_question(question_id):
    if request.method == "POST":
        comment = request.form.get("message")
        user_id = session['id']
        data_manager_questions.write_comment(question_id, comment, user_id)
        return redirect("/question/" + str(question_id))
    else:
        return render_template("comment_to_question.html", question_id=question_id)


@app.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    user_question = data_manager_questions.get_question_by_id(question_id)
    if request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        data_manager_questions.edit_question(title, message, question_id)
        blink_url = "/question/" + str(question_id)
        return redirect(blink_url)
    return render_template('edit_question.html', question=user_question, question_id=question_id)


@app.route('/answer/<int:answer_id>/edit', methods=['GET', 'POST'])
def edit_answer(answer_id):
    user_answer = data_manager_answers.get_answer(answer_id)
    if request.method == 'POST':
        message = request.form.get('message')
        data_manager_answers.edit_answer(message, answer_id)
        return redirect(url_for('question', question_id=user_answer['question_id']))
    return render_template('edit_answer.html', answer=user_answer)

@app.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
def edit_question_comment(comment_id):
    question_comment = data_manager_questions.get_comment_by_id(comment_id)
    if request.method == 'POST':
        message = request.form.get('message')
        data_manager_questions.edit_question_comment(message, comment_id)
        return redirect(url_for('question', question_id=question_comment['question_id']))

    return render_template('edit_comment.html', comment=question_comment)


@app.route('/question/<int:question_id>/delete', methods=['GET'])
def delete_question(question_id):
    data_manager_questions.delete_question(question_id)
    return redirect('/')


@app.route('/question/<int:question_id>/answer/<int:answer_id>/delete', methods=['GET'])
def delete_answer(question_id, answer_id):
    data_manager_answers.delete_answer(answer_id)
    return redirect(url_for('question', question_id=question_id))


@app.route('/question/<int:question_id>/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(question_id, comment_id):
    data_manager_questions.delete_comment(comment_id)
    return redirect(url_for('question', question_id=question_id))

@app.route('/question/<int:question_id>/vote-up')
def question_vote_up(question_id):
    user_id = session['id']
    data_manager_questions.vote_up_on_questions(question_id)
    data_manager_questions.gain_reputation(user_id)
    return redirect(url_for('question', question_id=question_id))

@app.route('/question/<int:question_id>/vote-down')
def question_vote_down(question_id):
    user_id = session['id']
    data_manager_questions.vote_down_on_questions(question_id)
    data_manager_questions.lose_reputation(user_id)
    return redirect(url_for('question', question_id=question_id))

@app.route('/answer/<int:answer_id>/vote-up')
def answer_vote_up(answer_id):
    user_id = session['id']
    answer = data_manager_answers.get_answer(answer_id)
    data_manager_answers.vote_up_on_answer(answer_id)
    data_manager_answers.gain_reputation(user_id)
    return redirect(url_for('question', question_id=answer['question_id']))

@app.route('/answer/<int:answer_id>/vote-down')
def answer_vote_down(answer_id):
    user_id = session['id']
    answer = data_manager_answers.get_answer(answer_id)
    data_manager_answers.vote_down_on_answer(answer_id)
    data_manager_answers.lose_reputation(user_id)
    return redirect(url_for('question', question_id=answer['question_id']))

@app.route('/search')
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
    return render_template('search.html', headers=util.QUESTION_HEADER, stories=search_results,
                           search_phrase=search_phrase)


@app.route('/question/<int:question_id>/new-tag', methods=['GET', 'POST'])
def add_tag_to_question(question_id):
    if request.method == 'GET':
        tags = data_manager_questions.get_all_tags()
        return render_template('add_tag.html', question_id=question_id, tags=tags)
    elif request.method == 'POST':
        new_tag = request.form.get('new_tag')
        data_manager_questions.add_new_tag(new_tag, question_id)
        return redirect(url_for('question', question_id=question_id))


@app.route('/question/<int:question_id>/tag/<tag_id>/delete')
def delete_tag_from_question(question_id, tag_id):
    data_manager_questions.tag_delete_from_question(question_id, tag_id)
    return redirect(url_for('question', question_id=question_id))

@app.route('/tags')
def tag_page():
    tags = data_manager_questions.get_tags_with_numbers()
    return render_template('tags.html', tags=tags)

@app.route("/question/<int:question_id>/answer/<int:answer_id>/new-comment", methods=['GET', 'POST'])
def comment_to_answer(answer_id, question_id):
    if request.method == "POST":
        answer_comment = request.form.get("message")
        user_id = session['id']
        data_manager_answers.add_comment_to_answer(question_id, answer_id, answer_comment, user_id)
        return redirect("/question/" + str(question_id))
    else:
        return render_template("comment_to_answer.html", answer_id=answer_id, question_id=question_id)

@app.route('/users')
def display_users_list():
    users_list = user_controller.get_users_list()
    print(users_list)
    headers = util.USER_HEADER
    if 'id' in session:
        return render_template("users.html", users_list=users_list, headers=headers)
    return render_template('main.html')

@app.route('/users/<user_id>')
def user_details(user_id):
    current_user_data = user_controller.get_current_user_data(user_id)[0]
    print(current_user_data)
    current_user_questions = user_controller.get_current_user_questions(user_id)
    current_user_answers = user_controller.get_current_user_answers(user_id)
    current_user_comments = user_controller.get_current_user_comments(user_id)
    if 'id' in session:
        return render_template('user_profile.html', user_id=user_id, current_user_data=current_user_data,
                                       current_user_questions=current_user_questions, current_user_answers=current_user_answers,
                                       logged_in=True, current_user_comments=current_user_comments)
    return render_template('main.html')

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = -1
if __name__ == "__main__":
    app.run(
        debug=True,
    )
