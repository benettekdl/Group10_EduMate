from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, Task, Reminder

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edumate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)
migrate = Migrate(app, db)


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------------------------------------
# ROUTES
# ---------------------------------------------

@app.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.due_date).all()
    return render_template('index.html', tasks=tasks)


# ----------------------------
# Authentication Routes
# ----------------------------

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        student_id = request.form['student_id']
        email = request.form['email']
        password = request.form['password']

        existing = User.query.filter_by(email=email).first()
        if existing:
            flash('Email already registered.', 'danger')
            return redirect(url_for('signup'))

        hashed_pw = generate_password_hash(password)
        username = email.split('@')[0]
        new_user = User(username=username, name=name, student_id=student_id, email=email, password=hashed_pw)

        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

        login_user(user)
        flash('Logged in successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Password reset instructions sent to your email (demo only).', 'info')
        else:
            flash('Email not found.', 'danger')
    return render_template('forgot_password.html')


# ----------------------------
# Task Management
# ----------------------------

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        task_type = request.form['task_type']
        due_date = datetime.fromisoformat(request.form['due_date'])
        notes = request.form.get('notes', '')

        new_task = Task(
            title=title,
            task_type=task_type,
            due_date=due_date,
            notes=notes,
            user_id=current_user.id
        )
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully.', 'success')
        return redirect(url_for('task_management'))
    return render_template('add_task.html')



@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = Task.query.get_or_404(id)

    if task.user_id != current_user.id:
        flash('You are not authorized to edit this task.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        task.title = request.form['title']
        task.task_type = request.form['task_type']
        task.due_date = datetime.fromisoformat(request.form['due_date'])
        task.notes = request.form.get('notes', '')
        db.session.commit()
        flash('Task updated.', 'success')
        return redirect(url_for('index'))

    return render_template('edit_task.html', task=task)


@app.route('/task/<int:id>/delete', methods=['POST'])
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('index'))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully.', 'success')
    return redirect(url_for('index'))



# -----------------------------
# REMINDER ROUTES
# -----------------------------
@app.route('/reminder')
@login_required
def reminder_page():
    reminders = Reminder.query.filter_by(user_id=current_user.id).order_by(Reminder.reminder_time.asc()).all()
    return render_template('reminder.html', reminders=reminders)

@app.route('/reminder/add', methods=['GET', 'POST'])
@login_required
def add_reminder():
    if request.method == 'POST':
        title = request.form['title']
        reminder_time = request.form['reminder_time']
        notes = request.form['notes']

        new_reminder = Reminder(
            title=title,
            reminder_time=datetime.strptime(reminder_time, '%Y-%m-%dT%H:%M'),
            notes=notes,
            user_id=current_user.id
        )
        db.session.add(new_reminder)
        db.session.commit()
        flash('Reminder added successfully!', 'success')
        return redirect(url_for('reminder_page'))

    return render_template('add_reminder.html')

@app.route('/reminder/<int:id>')
@login_required
def reminder_view(id):
    reminder = Reminder.query.get_or_404(id)
    if reminder.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('reminder_page'))
    return render_template('reminder_view.html', reminder=reminder)

@app.route('/reminder/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_reminder(id):
    reminder = Reminder.query.get_or_404(id)
    if reminder.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('reminder_page'))

    if request.method == 'POST':
        reminder.title = request.form['title']
        reminder.reminder_time = datetime.strptime(request.form['reminder_time'], '%Y-%m-%dT%H:%M')
        reminder.notes = request.form['notes']
        db.session.commit()
        flash('Reminder updated successfully!', 'success')
        return redirect(url_for('reminder_page'))

    return render_template('edit_reminder.html', reminder=reminder)

@app.route('/reminder/<int:id>/delete', methods=['POST'])
@login_required
def delete_reminder(id):
    reminder = Reminder.query.get_or_404(id)
    if reminder.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('reminder_page'))

    db.session.delete(reminder)
    db.session.commit()
    flash('Reminder deleted successfully.', 'success')
    return redirect(url_for('reminder_page'))




# ----------------------------
# User Profile
# ----------------------------

@app.route('/profile')
@login_required
def profile():
    return render_template('user_profile.html')


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.student_id = request.form['student_id']
        current_user.email = request.form['email']
        new_pw = request.form['password']

        if new_pw:
            current_user.password = generate_password_hash(new_pw)

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))
    return render_template('edit_profile.html')



# ----------------------------
# FAQs
# ----------------------------

@app.route('/faqs')
@login_required
def faqs():
    return render_template('faqs.html')



@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')


@app.route('/task/<int:id>')
@login_required
def view_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
    return render_template('task_view.html', task=task)

@app.route('/tasks')
@login_required
def task_management():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.due_date).all()
    return render_template('task_management.html', tasks=tasks)


# ---------------------------------------------
# MAIN ENTRY
# ---------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
