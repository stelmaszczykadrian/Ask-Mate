from operator import itemgetter
from flask import Flask, render_template, request, url_for, redirect
from bonus_questions import SAMPLE_QUESTIONS

from markupsafe import Markup
import users_manager
import data_manager_answers
import data_manager_questions
import util

app = Flask(__name__)

@app.route("/bonus-questions")
def bonus_question():
    return render_template('bonus_questions.html', questions=SAMPLE_QUESTIONS)


@app.route("/", methods=['GET'])
def main():
    user_questions = data_manager_questions.get_latest_questions()
    # all_questions_data = data_manager_questions.get_question_data()
    return render_template('main.html', headers=util.QUESTION_HEADER, stories=user_questions)


@app.route('/list', methods=['GET'])
def route_list():
    order_by = request.args.get('order_by', 'submission_time')
    order_direction = request.args.get("order_direction", 'asc')
    user_questions = data_manager_questions.get_question_data()
    for question in user_questions:
        question['view_number'] = int(question['view_number'])
        question['vote_number'] = int(question['vote_number'])

    sorted_questions_by_recent = sorted(user_questions, key=itemgetter(
        order_by), reverse=order_direction == 'desc')
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
    return render_template('question.html', question=user_question, answers=user_answers,
                           user_comments_to_questions=user_comments_to_questions, question_id=question_id,
                           tags=data_manager_questions.get_tags(question_id))


@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        id = data_manager_questions.add_question(title, message)
        return redirect(url_for('question', question_id=id['id']))
    return render_template('add-question.html')


@app.route('/question/<int:question_id>/new-answer', methods=['GET', 'POST'])
def add_answer(question_id):
    if request.method == 'POST':
        message = request.form.get('message')
        data_manager_answers.add_answer(message, question_id)
        return redirect(url_for('question', question_id=question_id))
    return render_template('new-answer.html', question_id=question_id)


@app.route("/question/<int:question_id>/new-comment", methods=['GET', 'POST'])
def comment_to_question(question_id):
    if request.method == "POST":
        comment = request.form.get("message")
        data_manager_questions.add_new_comment(question_id, comment)

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


# jeszcze nie działa :<
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
    data_manager_questions.vote_up_on_questions(question_id)
    blink_url = "/question/" + str(question_id)
    return redirect(blink_url)


@app.route('/question/<int:question_id>/vote-down')
def question_vote_down(question_id):
    data_manager_questions.vote_down_on_questions(question_id)
    blink_url = "/question/" + str(question_id)
    return redirect(blink_url)


@app.route('/answer/<int:answer_id>/vote-up')
def answer_vote_up(answer_id):
    answer = data_manager_answers.get_answer(answer_id)
    data_manager_answers.vote_up_on_answer(answer_id)
    blink_url = "/question/" + str(answer['question_id'])
    return redirect(blink_url)


@app.route('/answer/<int:answer_id>/vote-down')
def answer_vote_down(answer_id):
    answer = data_manager_answers.get_answer(answer_id)
    data_manager_answers.vote_down_on_answer(answer_id)
    blink_url = "/question/" + str(answer['question_id'])
    return redirect(blink_url)


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


@app.route("/question/<int:question_id>/answer/<int:answer_id>/new-comment", methods=['GET', 'POST'])
def comment_to_answer(answer_id, question_id):
    if request.method == "POST":
        answer_comment = request.form.get("message")
        data_manager_answers.add_comment_to_answer(answer_comment, answer_id, question_id)
        return redirect("/question/" + str(question_id))
    else:
        return render_template("comment_to_answer.html", answer_id=answer_id, question_id=question_id)

@app.route('/users')
def display_users_list():
    users_list = users_manager.get_users_list()
    headers = util.USER_HEADER
    return render_template("users.html", users_list=users_list, headers=headers)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = -1
if __name__ == "__main__":
    app.run(
        debug=True,
    )
