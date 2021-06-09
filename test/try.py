# questions = [
#     {
#         "id": "1",
#         "question": "What is the Capital of Syria?",
#         "answers": ["a) Beirut", "b) Damascus", "c) Baghdad"],
#         "correct": "b) Damascus"
#     },
#     {
#         "id": "2",
#         "question": "What is the square root of Pi?",
#         "answers": ["a) 1.7724", "b) 1.6487", "c) 1.7872"],
#         "correct": "a) 1.7724"
#     },
#     {
#         "id": "3",
#         "question": "How many counties are there in England?",
#         "answers": ["a) 52", "b) 48", "c) 45"],
#         "correct": "b) 48"
#     }
# ]

# @app.route("/quiz", methods=['POST', 'GET'])
# @login_required
# def quiz():
#     if current_user.is_authenticated:
#         if request.method == 'GET':
#             return render_template("quiz.html", data=questions)
#         else:
#             result = 0
#             total = 0
#             for question in questions:
#                 if request.form[question.get('id')] == question.get('correct'):
#                     result += 1
#                 total += 1
#             return render_template('results.html', total=total, result=result)
#     else:
#         message = 'Signup to continue'
#         return render_template('signup.html', message=message)


# @app.route("/delete-one-appointment", methods=['GET', 'POST'])
# @login_required
# def dcalendar():
#     if current_user.is_authenticated:
#         rooms = get_rooms_for_user(current_user.username)
#         if rooms == []:
#             return render_template('home.html', message = "Please join a room to delete an appointment")
#         else:
#             c = ["Bhavana Bhasin", "Kamiya Kumar", "Tanvi Bajaj"]
#             for co in c:
#                 if co != current_user.username:
#                     if request.method == 'POST':
#                         date = request.form.get('date')
#                         timestart = request.form.get('timestart')
#                         timeend = request.form.get('timeend')
#                         rooms = get_rooms_for_user(current_user.username)
#                         event = rooms[0].get('room_name')[13:]
#                         s = rooms[0].get('room_name').split()
#                         x = ""
#                         x += s[4]
#                         x += " "
#                         x += s[5]
#                         members = x
#                         delete_event(date, timestart, timeend, event, current_user.username, members)
#                         return redirect(url_for('schedule'))
#                     return render_template('calendar.html')
#                 else:
#                     return render_template('schedule.html', message = "Only students can access this page")
#     else:
#         return render_template('home.html', message = "Login to continue")


# @app.route("/delete-group-appointment", methods=['GET', 'POST'])
# @login_required
# def dgcalendar():
#     if current_user.is_authenticated:
#         c = ["Bhavana Bhasin", "Kamiya Kumar", "Tanvi Bajaj"]
#         if current_user.username in c:
#             if request.method == 'POST':
#                 date = request.form.get('date')
#                 timestart = request.form.get('timestart')
#                 timeend = request.form.get('timeend')
#                 event = request.form.get('event')
#                 delete_gevent(date, timestart, timeend, event)
#                 return render_template('home.html')
#             return render_template('gcalendar.html')
#         else:
#             return render_template('home.html', message = "Only counsellors can access this page")
#     else:
#         return render_template('home.html', message = "Login to continue")

