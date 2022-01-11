from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, join_room, leave_room
from pymongo.errors import DuplicateKeyError
from mongodb import get_user, save_user, save_room, add_room_members, get_rooms_for_user, is_room_member
from mongodb import get_room_members, save_message, get_messages, get_room, update_user
from mysqldb import get_videoss, insert_group, get_group, get_none_teacher
from mysqldb import get_added_by, insert_one_c, get_quote, get_date_members
from mysqldb import insert_one, get_nevent_id, insert_app, delete_column, get_addedby_members


app = Flask(__name__)
app.secret_key = "granthbagadiagranthbagadia"
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

c = ["Bhavana Bhasin", "Kamiya Kumar", "Tanvi Bajaj", "G-ADMIN", "S-ADMIN"]

@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    return render_template('home.html', message = get_quote())


@app.route("/request-app", methods=['GET', 'POST'])
@login_required
def request_app():
    message = ""
    return render_template('request_app.html', message=message)


@app.route("/schedule", methods=['GET', 'POST'])
@login_required
def schedule():
    message = ""
    return render_template('schedule.html', message = message)


@app.route("/notifications", methods=['GET', 'POST'])
@login_required
def notifications():
    if current_user.username in c:
        nevents = get_none_teacher(current_user.username)
        return render_template('notification_teacher.html', nevents = nevents)
    elif current_user.username not in c:
        napprovals = get_added_by(current_user.username)
        return render_template('notification_student.html', napprovals = napprovals[::-1])


@app.route("/pic", methods=['GET', 'POST'])
@login_required
def pic():
    message = ""
    if current_user.is_authenticated:
        return render_template('pic.html', videos = get_videoss()[0:-1], message = message)
    else:
        return render_template('home.html', message = "Login to continue")


@app.route('/view-rooms', methods=['GET', 'POST'])
@login_required
def rooms():
    rooms_list = []
    message = ""
    if current_user.is_authenticated:
        rooms_list = get_rooms_for_user(current_user.username)
        return render_template("view_rooms.html", rooms=rooms_list, message = message)
    else:
        return render_template('home.html', message = "Login to continue")


@app.route('/chat-room/<room_id>/', methods=['GET', 'POST'])
@login_required
def view_room(room_id):
    room_get = get_room(room_id)
    link = ""
    if room_get and is_room_member(room_id, current_user.username):
        room_members = get_room_members(room_id)
        messages = get_messages(room_id)
        a = ""
        for i in messages:
            a += i.get("sender")
            a += " - "
            a += i.get("text")
            a += " \n"

        return render_template('chat_room.html', username=current_user.username, room=room_get, room_members=room_members,messages=messages, down = a)
    else:
        return "Room not found", 404


@app.route("/new-one", methods=['GET', 'POST'])
@login_required
def new_one():
    if current_user.is_authenticated:
        rooms_list = get_rooms_for_user(current_user.username)
        if rooms_list == []:
            return render_template('request_app.html', message = "Please join a counsellor to request for a meet.")
        else:
            rooms = get_rooms_for_user(current_user.username)
            xy = rooms[0].get('_id').get('room_id')
            xyz = get_room_members(xy)
            x = xyz[1].get('_id').get('username')
            c = ["Bhavana Bhasin", "Kamiya Kumar", "Tanvi Bajaj", "G-ADMIN", "S-ADMIN"]
            if current_user.username not in c:
                if request.method == 'POST':
                    datee = request.form.get('date')
                    if datee == "":
                        return render_template('new_one.html',counsellor = "", message = "Please enter a date")
                    else:
                        date = f'{datee[6:]}-{datee[0:2]}-{datee[3:5]}'
                        sl = ['10:00-10:30', '10:30-11:00', '11:00-11:30', '11:30-12:00', '12:00-12:30', '12:30-13:00', '13:00-13:30']
                        busy = []
                        members = get_rooms_for_user(current_user.username)
                        xy = members[0].get('_id').get('room_id')
                        xyz = get_room_members(xy)
                        x = xyz[1].get('_id').get('username')
                        e = get_date_members(date, x)
                        for i in e:
                            time = i[2]
                            busy.append(time)
                        options = [item for item in sl if item not in busy]
                        if options == []:
                            return render_template('new_one.html', counsellor = x, message = f"All slots are booked for {c}")
                        else:
                            return redirect(url_for('x', date = date))
                return render_template('new_one.html', counsellor = x, message = "")
            else:
                return render_template('request_app.html', message = "Only Students can access this page")
    else:
        return render_template('home.html', message = "Login to continue")


@app.route("/x/<date>", methods=['GET', 'POST'])
def x(date):
    sl = ['10:00-10:30', '10:30-11:00', '11:00-11:30', '11:30-12:00', '12:00-12:30', '12:30-13:00', '13:00-13:30']
    busy = []
    members = get_rooms_for_user(current_user.username)
    xy = members[0].get('_id').get('room_id')
    xyz = get_room_members(xy)
    x = xyz[1].get('_id').get('username')
    e = get_date_members(date, x)
    for i in e:
        time = i[2]
        busy.append(time)
    options = [item for item in sl if item not in busy]
    if request.method == 'POST':
        timestart = request.form.get('slot')
        rooms = get_rooms_for_user(current_user.username)
        ew = rooms[0].get('room_name')[13:]
        em = request.form.get('event')
        event = f"Meet of {ew} regarding {em}"
        s = rooms[0].get('room_name').split()
        members = f"{s[4]} {s[5]}"
        insert_one_c(date, timestart, event, current_user.username, members)
        return render_template('request_app.html', message = "Your request has been sent")
    return render_template('x.html', options = options, date = date)


@app.route('/check-one', methods=['GET', 'POST'])
@login_required
def check_one():
    if current_user.is_authenticated:
        rooms_list = get_rooms_for_user(current_user.username)
        if rooms_list == []:
            return render_template('schedule.html', message = "Please join a counsellor to check for meets.")
        else:
            events = get_addedby_members(current_user.username)
            events_list = []
            members = get_rooms_for_user(current_user.username)
            xy = members[0].get('_id').get('room_id')
            xyz = get_room_members(xy)
            x = xyz[1].get('_id').get('username')
            for event in events:
                date = event[1]
                rooms = get_rooms_for_user(current_user.username)
                eventt = event[3]
                timestart = event[2]
                time = timestart
                link = ""
                if x == "S-ADMIN":
                    link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                if x == "Bhavana Bhasin":
                    link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                if x == "Tanvi Baja":
                    link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                if x == "Kamiya Kumar":
                    link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                event = eventt + " " + link
                e = [event, date, time]
                events_list.append(e)
            if current_user.username not in c:
                events_cs = get_addedby_members(x)
                for event_c in events_cs:
                    date_c = event_c[1]
                    eventt_c = f"Slot booked for Ms. {x}"
                    timestart_c = event_c[2]
                    time_c = timestart_c
                    e_c = [eventt_c, date_c, time_c]
                    if event_c[4] == current_user.username:
                        pass
                    else:
                        events_list.append(e_c)
            return render_template("check_one.html", gevents=events_list)
    else:
        return render_template('home.html', message = "Login to continue")


@app.route('/counsellor/<x>', methods=['GET', 'POST'])
@login_required
def counsellor(x):
    if current_user.is_authenticated:
        if x == '<1>':
            x = "Bhavana Bhasin"
        elif x == '<2>':
            x = "Kamiya Kumar"
        elif x == '<3>':
            x = "Tanvi Bajaj"
        room_name = "Chat room of Ms. " + x + " with " + current_user.username
        if current_user.is_authenticated:
            rooms = get_rooms_for_user(current_user.username)
            for room in rooms:
                if room['room_name'] == room_name:
                    room_id = room['_id']['room_id']
                    return redirect(url_for('view_room', room_id=room_id))
            else:
                usernames = [x , current_user.username]
                room_id = save_room(room_name, current_user.username)
                if current_user.username in usernames:
                    usernames.remove(current_user.username)
                add_room_members(room_id, room_name, usernames, current_user.username)
                return redirect(url_for('view_room', room_id=room_id))
        else:
            return "You can not create a room", 404
    else:
        return render_template('home.html', message = "Login to continue")


@app.route("/addnevent/<x>", methods=['GET', 'POST'])
@login_required
def addnevent(x):
    a = get_nevent_id(x)[0]
    added_by = a[4]
    date = a[1]
    timestart = a[2]
    members = a[5]
    event = a[3]
    insert_one(date, timestart, event, added_by, members)
    info = f"Your meet with {members} on {date} regarding {event} has been scheduled betweeen {timestart}"
    insert_app(info, added_by)
    delete_column(x)
    return render_template('home.html', message = "Thanks for your response.")


@app.route("/noaddnevent/<x>", methods=['GET', 'POST'])
@login_required
def noaddnevent(x):
    a = get_nevent_id(x)[0]
    added_by = a[4]
    timestart = a[2]
    info = f"The time slot {timestart} is not available"
    insert_app(info, added_by)
    delete_column(x)
    return render_template('home.html', message = "Thanks for your response.")


@app.route("/new-group", methods=['GET', 'POST'])
@login_required
def new_group():
    message = ""
    if current_user.is_authenticated:
        q = get_group()
        r = 0
        c = ["Bhavana Bhasin", "Kamiya Kumar", "Tanvi Bajaj", "ADMIN", "G-ADMIN", "S-ADMIN"]
        if current_user.username in c:
            if request.method == 'POST':
                date = request.form.get('date')
                timestart = request.form.get('timestart')
                timeend = request.form.get('timeend')
                event = request.form.get('event')
                link = request.form.get('link')
                if timeend > timestart:
                    for w in q:
                        ts = w[2]
                        te = w[3]
                        if date == w[1]:
                            if timestart >= ts and timestart <= te:
                                message = "This slot has already been booked"
                                r += 1
                                return render_template('new_group.html', message = message)
                            elif timeend >= ts and timeend <= te:
                                message = "This slot has already been booked"
                                r += 1
                                return render_template('new_group.html', message = message)
                    if r == 0:
                        insert_group(date, timestart, timeend, event, link)
                        return render_template('request_app.html', message="Meeting Scheduled")
                else:
                    return render_template('new_group.html', message = "Ending time has to be after start time")
            return render_template('new_group.html', message = message)
        else:
            return render_template('request_app.html', message = "Only counsellors can access this page")
    else:
        return render_template('home.html', message = "Login to continue")


@app.route('/check-group/', methods=['GET', 'POST'])
@login_required
def check_group():
    if current_user.is_authenticated:
        return render_template("check_group.html", gevents=get_group())
    else:
        return render_template('home.html', message = "Login to continue")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            save_user(username, email, password)
            return redirect(url_for('login'))
        except DuplicateKeyError:
            message = "User already exists!"
    return render_template('signup.html', message=message)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')
        user = get_user(username)
        if user and user.check_password(password_input):
            login_user(user)
            return redirect(url_for('home'))
        else:
            message = 'Failed to login!'
    return render_template('login.html', message=message)


@app.route("/logout/", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/change-pass', methods=['GET', 'POST'])
@login_required
def change_pass():
    message = ''
    if request.method == 'POST':
        new_pass = request.form.get('new_pass')
        update_user(current_user.username, current_user.email, new_pass)
        message = 'Password Changed successfully'
    return render_template('change_pass.html', message = message)


@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'],
                                                                    data['room'],
                                                                    data['message']))
    data['created_at'] = datetime.now().strftime("%d %b, %H:%M")
    save_message(data['room'], data['message'], data['username'])
    socketio.emit('receive_message', data, room=data['room'])


@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data, room=data['room'])


@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room'])


@login_manager.user_loader
def load_user(username):
    return get_user(username)


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


@app.errorhandler(404)
def page_not_found(e):
    return render_template('500.html'), 404


if __name__ == '__main__':
    socketio.run(app, debug=True)