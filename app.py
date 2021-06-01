from datetime import datetime
from dns.message import Message
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, join_room, leave_room
from pymongo.errors import DuplicateKeyError
from db import get_user, save_user, save_room, add_room_members, get_rooms_for_user, get_room, is_room_member
from db import get_room_members, is_room_admin, update_room, remove_room_members, save_message, get_messages, get_events_for_user_date
from db import add_event, get_events_for_user, get_gevents, add_gevent, update_user, get_video, delete_event, delete_gevent
from db import add_nevent, get_nevents_for_user, get_nevents_by_id, delete_nevents_by_id, add_napproval_for_user, get_napproval_for_user

app = Flask(__name__)
app.secret_key = "granthbagadiagranthbagadia"
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)



@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    message = ""
    return render_template('home.html', message = message)


@app.route("/granth", methods=['GET', 'POST'])
def granth():
    return render_template('granth.html')


@app.route("/notifications", methods=['GET', 'POST'])
@login_required
def notifications():
    c = ["Bhavana Bhasin", "Kamiya Kumar", "Tanvi Bajaj"]
    if current_user.username in c:
        nevents = get_nevents_for_user(current_user.username)
        return render_template('notification_teacher.html', nevents = nevents)
    elif current_user.username not in c:
        napprovals = get_napproval_for_user(current_user.username)
        return render_template('notification_student.html', napprovals = napprovals[::-1])


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


@app.route("/pic", methods=['GET', 'POST'])
@login_required
def pic():
    videos = ""
    message = ""
    if current_user.is_authenticated:
        videos_db = get_video()
        for video in videos_db:
            x = video.get('video')
            videos += x
            videos += ","
        return render_template('pic.html', videos = videos[0:-1], message = message)
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


@app.route("/new-one", methods=['GET', 'POST'])
@login_required
def new_one():
    if current_user.is_authenticated:
        rooms = get_rooms_for_user(current_user.username)
        xy = rooms[0].get('_id').get('room_id')
        xyz = get_room_members(xy)
        x = xyz[1].get('_id').get('username')
        if rooms == []:
            return render_template('home.html', message = "Please join a room to schedule a meet")
        else:
            c = ["Bhavana Bhasin", "Kamiya Kumar", "Tanvi Bajaj", "G-ADMIN", "S-ADMIN"]
            if current_user.username not in c:
                if request.method == 'POST':
                    c = request.form.get('date')
                    date = f'{c[6:]}-{c[0:2]}-{c[3:5]}'
                    return redirect(url_for('x', date = date))
                return render_template('new_one.html', counsellor = x)
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
    e = get_events_for_user_date(x, date)
    for i in e:
        time = i.get('timestart')
        busy.append(time)
    options = [item for item in sl if item not in busy]
    if request.method == 'POST':
        timestart = request.form.get('slot')
        print(timestart)
        rooms = get_rooms_for_user(current_user.username)
        event = rooms[0].get('room_name')[13:]
        s = rooms[0].get('room_name').split()
        members = f"{s[4]} {s[5]}"
        print(date, timestart, event, current_user.username, members)
        add_nevent(date, timestart, event, current_user.username, members)
        return render_template('request_app.html', message = "Your request has been sent")
    return render_template('x.html', options = options, date = date)


@app.route("/new-group", methods=['GET', 'POST'])
@login_required
def new_group():
    message = ""
    if current_user.is_authenticated:
        q = get_gevents()
        r = 0
        c = ["Bhavana Bhasin", "Kamiya Kumar", "Tanvi Bajaj", "ADMIN", "G-ADMIN", "S-ADMIN"]
        if current_user.username in c:
            if request.method == 'POST':
                date = request.form.get('date')
                timestart = request.form.get('timestart')
                timeend = request.form.get('timeend')
                event = request.form.get('event')
                link = request.form.get('link')
                print(timestart, timeend)
                if timeend > timestart:
                    for w in q:
                        ts = w.get('timestart')
                        te = w.get('timeend')
                        if date == w.get('date'):
                            if timestart >= ts and timestart <= te:
                                message = "This slot has already been booked"
                                r += 1
                                return render_template('new_group.html', message = message)
                            elif timeend >= ts and timeend <= te:
                                message = "This slot has already been booked"
                                r += 1
                                return render_template('new_group.html', message = message)
                    if r == 0:
                        add_gevent(date, timestart, timeend, event, link)
                        return render_template('request_app.html', message="Meeting Scheduled")
                else:
                    return render_template('new_group.html', message = "Ending time has to be after start time")
            return render_template('new_group.html', message = message)
        else:
            return render_template('request_app.html', message = "Only counsellors can access this page")
    else:
        return render_template('home.html', message = "Login to continue")


@app.route('/check-one', methods=['GET', 'POST'])
@login_required
def check_one():
    if current_user.is_authenticated:
        events = get_events_for_user(current_user.username)
        events_list = []
        members = get_rooms_for_user(current_user.username)
        xy = members[0].get('_id').get('room_id')
        xyz = get_room_members(xy)
        x = xyz[1].get('_id').get('username')
        c = ["Bhavana Bhasin", "Kamiya Kumar", "Tanvi Bajaj", "G-ADMIN", "S-ADMIN"]
        for event in events:
            date = event['date']
            rooms = get_rooms_for_user(current_user.username)
            eventt = event.get('event')
            timestart = event.get('timestart')
            time = timestart
            link = ""
            if x == "S-ADMIN":
                link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            if x == "Bhavana Bhasin":
                link = "https://us04web.zoom.us/j/74664083392?pwd=TGlncmNTeUJoRXdYckpHNXArRit5UT09#success"
            if x == "Tanvi Baja":
                link = "https://us04web.zoom.us/j/74664083392?pwd=TGlncmNTeUJoRXdYckpHNXArRit5UT09#success"
            if x == "Kamiya Kumar":
                link = "https://us04web.zoom.us/j/74664083392?pwd=TGlncmNTeUJoRXdYckpHNXArRit5UT09#success"
            event = eventt + " " + link
            e = [event, date, time]
            events_list.append(e)
        if current_user.username not in c:
            events_cs = get_events_for_user(x)
            for event_c in events_cs:
                print(event_c.get('added_by'))
                date_c = event_c.get('date')
                eventt_c = f"Slot booked for Ms. {x}"
                timestart_c = event_c.get('timestart')
                time_c = timestart_c
                e_c = [eventt_c, date_c, time_c]
                if event_c.get('added_by') == current_user.username:
                    pass
                else:
                    events_list.append(e_c)
        return render_template("check_one.html", gevents=events_list)
    else:
        return render_template('home.html', message = "Login to continue")


@app.route('/check-group/', methods=['GET', 'POST'])
@login_required
def check_group():
    if current_user.is_authenticated:
        gevents = get_gevents()
        gevents_list = []
        for gevent in gevents:
            date = gevent['date']
            eventt = gevent['event']
            timestart = gevent['timestart']
            timeend = gevent['timeend']
            time = timestart+"-"+timeend
            link = gevent['link']
            event = eventt + " " + link
            g = [event, date, time, link]
            gevents_list.append(g)
        return render_template("check_group.html", gevents=gevents_list)
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
    nevents = get_nevents_by_id(x)
    objInstance = x
    added_by = get_nevents_by_id(objInstance)[0].get('added_by')
    date = get_nevents_by_id(objInstance)[0].get('date')
    timestart = get_nevents_by_id(objInstance)[0].get('timestart')
    members = get_nevents_by_id(objInstance)[0].get('members')
    event = get_nevents_by_id(objInstance)[0].get('event')
    add_event(date, timestart, event, added_by, members)
    info = f"Your meet with {members} on {date} has been scheduled betweeen {timestart}"
    add_napproval_for_user(info, added_by)
    delete_nevents_by_id(x)
    return render_template('home.html')


@app.route("/noaddnevent/<x>", methods=['GET', 'POST'])
@login_required
def noaddnevent(x):
    nevents = get_nevents_by_id(x)
    objInstance = x
    added_by = get_nevents_by_id(objInstance)[0].get('added_by')
    date = get_nevents_by_id(objInstance)[0].get('date')
    timestart = get_nevents_by_id(objInstance)[0].get('timestart')
    members = get_nevents_by_id(objInstance)[0].get('members')
    event = get_nevents_by_id(objInstance)[0].get('event')
    info = "This time slot is not available"
    add_napproval_for_user(info, added_by)
    delete_nevents_by_id(x)
    return render_template('home.html')


@app.route("/logout/", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/chat-room/<room_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_room(room_id):
    room = get_room(room_id)
    if room and is_room_admin(room_id, current_user.username):
        existing_room_members = [member['_id']['username'] for member in get_room_members(room_id)]
        room_members_str = ",".join(existing_room_members)
        message = ''
        if request.method == 'POST':
            room_name = request.form.get('room_name')
            room['name'] = room_name
            update_room(room_id, room_name)
            new_members = [username.strip() for username in request.form.get('members').split(',')]
            members_to_add = list(set(new_members) - set(existing_room_members))
            members_to_remove = list(set(existing_room_members) - set(new_members))
            if len(members_to_add):
                add_room_members(room_id, room_name, members_to_add, current_user.username)
            if len(members_to_remove):
                remove_room_members(room_id, members_to_remove)
            message = 'Room edited successfully'
            room_members_str = ",".join(new_members)
        return render_template('edit_room.html', room=room, room_members_str=room_members_str, message=message)
    else:
        return "Only the room admin can edit the room details ", 404


@app.route('/change-pass', methods=['GET', 'POST'])
@login_required
def change_pass():
    message = ''
    if request.method == 'POST':
        new_pass = request.form.get('new_pass')
        update_user(current_user.username, current_user.email, new_pass)
        message = 'Password Changed successfully'
    return render_template('change_pass.html', message = message)


@app.route('/chat-room/<room_id>/', methods=['GET', 'POST'])
@login_required
def view_room(room_id):
    room_get = get_room(room_id)
    link = ""
    if room_get and is_room_member(room_id, current_user.username):
        room_members = get_room_members(room_id)
        messages = get_messages(room_id)
        return render_template('chat_room.html', username=current_user.username, room=room_get, room_members=room_members,messages=messages)
    else:
        return "Room not found", 404


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




@app.route('/index/', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.is_authenticated:
        gevents = get_gevents()
        gevents_list = []
        for gevent in gevents:
            date = gevent['date']
            eventt = gevent['event']
            timestart = gevent['timestart']
            timeend = gevent['timeend']
            time = timestart+"-"+timeend
            link = gevent['link']
            event = eventt + " " + link
            g = [event, date, time, link]
            gevents_list.append(g)
        return render_template("index.html", gevents = gevents_list)
    else:
        return render_template('home.html', message = "Login to continue")



if __name__ == '__main__':
    app.run()
