from flask import Flask, render_template, request, url_for, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import user_controller, data_manager_answers, data_manager_questions, logic
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
    invalid_credentials = False
    if request.method == "POST":
        user_name = request.form['email']
        password = request.form['psw']
        user_data = user_controller.get_user_password(user_name)
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
    new_user = {}
    if request.method == "POST":
        if len(request.form['email']) > 4 \
                and len(request.form['psw']) > 3:
            hash = generate_password_hash(request.form['psw'])
            new_user['user_name'] = request.form['email']
            new_user['password'] = hash
            new_user['registration_date'] = logic.get_time()
            user_controller.addUser(new_user)
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
    if 'id' in session:
        return render_template('bonus-questions.html', questions=SAMPLE_QUESTIONS, logged_user = get_logged_user())
    return render_template('bonus-questions.html', questions=SAMPLE_QUESTIONS)

@app.route("/", methods=['GET'])
def main():
    user_questions = data_manager_questions.get_latest_questions()
    if 'id' in session:
        return render_template('main.html', headers=data_manager_questions.QUESTION_HEADER, stories=user_questions, logged_user = get_logged_user())
    return render_template('main.html')

@app.route("/logout")
def logout():
    session.pop('id', None)
    session.pop('user_name', None)
    return redirect(url_for("login"))

@app.route('/list', methods=['GET'])
def route_list():
    sorted_questions_by_recent, order_by, order_direction, user_questions = logic.list_questions()

    return render_template('list.html', headers=data_manager_questions.QUESTION_HEADER,
                           stories=sorted_questions_by_recent,
                           order_by=order_by, order_direction=order_direction, questions=user_questions)

@app.route('/question/<int:question_id>', methods=['GET'])
def question(question_id):
    user_question, user_answers, user_comments_to_questions = logic.display_question(question_id)

    return render_template('question.html', question=user_question, answers=user_answers,
                           user_comments_to_questions=user_comments_to_questions, question_id=question_id,
                           tags=data_manager_questions.get_tags(question_id), logged_user = get_logged_user())

@app.route('/questions', methods=['GET'])
def all_questions():
    user_questions = data_manager_questions.get_latest_questions()
    if 'id' in session:
        return render_template('questions.html', headers=data_manager_questions.QUESTION_HEADER, stories=user_questions, logged_user = get_logged_user())
    return render_template('questions.html')

@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST' :
        id = logic.add_question()
        return redirect(url_for('question', question_id=id['id']))
    return render_template('add-question.html')

@app.route('/question/<int:question_id>/new-answer', methods=['GET', 'POST'])
def add_answer(question_id):
    if request.method == 'POST':
        logic.add_answer(question_id)
        return redirect(url_for('question', question_id=question_id))
    return render_template('new-answer.html', question_id=question_id)

@app.route("/question/<int:question_id>/new-comment", methods=['GET', 'POST'])
def comment_to_question(question_id):
    if request.method == "POST":
        logic.add_comment_to_question(question_id)
        return redirect(url_for('question', question_id=question_id))
    else:
        return render_template("comment_to_question.html", question_id=question_id)

@app.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    user_question = data_manager_questions.get_question_by_id(question_id)
    if request.method == 'POST':
        logic.edit_question(question_id)
        return redirect(url_for('question', question_id=question_id))
    return render_template('edit_question.html', question=user_question, question_id=question_id)

@app.route('/answer/<int:answer_id>/edit', methods=['GET', 'POST'])
def edit_answer(answer_id):
    user_answer = data_manager_answers.get_answer(answer_id)
    if request.method == 'POST':
        logic.edit_answer(answer_id)
        return redirect(url_for('question', question_id=user_answer['question_id']))
    return render_template('edit_answer.html', answer=user_answer)

@app.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
def edit_question_comment(comment_id):
    question_comment = data_manager_questions.get_comment_by_id(comment_id)
    if request.method == 'POST':
        logic.edit_question_comment(comment_id)
        return redirect(url_for('question', question_id=question_comment['question_id']))
    return render_template('edit_comment.html', comment=question_comment)

@app.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
def edit_answer_comment(comment_id):
    answer_comment = data_manager_questions.get_comment_by_id(comment_id)
    if request.method == 'POST':
        logic.edit_answer_comment(comment_id)
        return redirect(url_for('question', question_id=answer_comment['answer_id']))
    return render_template('edit_comment.html', comment=answer_comment)

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
    logic.question_vote_up(question_id)
    return redirect(url_for('question', question_id=question_id))

@app.route('/question/<int:question_id>/vote-down')
def question_vote_down(question_id):
    logic.question_vote_down(question_id)
    return redirect(url_for('question', question_id=question_id))

@app.route('/answer/<int:answer_id>/vote-up')
def answer_vote_up(answer_id):
    answer = answer_vote_up(answer_id)
    return redirect(url_for('question', question_id=answer['question_id']))

@app.route('/answer/<int:answer_id>/vote-down')
def answer_vote_down(answer_id):
    answer = answer_vote_down(answer_id)
    return redirect(url_for('question', question_id=answer['question_id']))

@app.route('/search')
def search():
    search_results, search_phrase = logic.search()
    return render_template('search.html', headers=data_manager_questions.QUESTION_HEADER, stories=search_results,
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
    if 'id' in session:
        return render_template('tags.html', tags=tags, logged_user = get_logged_user())
    return render_template('tags.html', tags=tags)

@app.route("/question/<int:question_id>/answer/<int:answer_id>/new-comment", methods=['GET', 'POST'])
def comment_to_answer(answer_id, question_id):
    if request.method == "POST":
        logic.add_comment_to_answer(answer_id, question_id)
        return redirect(url_for('question', question_id=question_id))
    else:
        return render_template("comment_to_answer.html", answer_id=answer_id, question_id=question_id)

@app.route('/users')
def display_users_list():
    users_list = user_controller.get_users_list()
    if 'id' in session:
        return render_template("users.html", users_list=users_list, headers=user_controller.USER_HEADER, logged_user = get_logged_user())
    return render_template('main.html')

@app.route('/users/<user_id>')
def user_details(user_id):
    current_user_data, current_user_questions, current_user_answers, current_user_comments = logic.user_details(user_id)
    if 'id' in session:
        return render_template('user_profile.html', user_id=user_id, current_user_data=current_user_data,
                                       current_user_questions=current_user_questions, current_user_answers=current_user_answers,
                                       logged_in=True, current_user_comments=current_user_comments, logged_user = get_logged_user())
    return render_template('main.html')

@app.route('/accept-answer/<answer_id>', methods=['POST'])
def accept_answer(answer_id):
    logic.accept_answer(answer_id)
    return redirect(url_for("question", question_id=data_manager_questions.get_question_by_answer_id(answer_id)['question_id']))

if __name__ == "__main__":
    app.run(
        debug=True,
    )