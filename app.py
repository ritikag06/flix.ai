from flask import Flask, render_template, request
import openai
import random


app = Flask(__name__)

# Default calendar data
calendar = {
    'Sunday': [],
    'Monday': [],
    'Tuesday': [],
    'Wednesday': [],
    'Thursday': [],
    'Friday': [],
    'Saturday': []
}


def schedule_task(task_name, task_duration, task_deadline, sleep_start_time, wake_up_time):
    # Sort the calendar days by availability (number of events)
    sorted_days = sorted(calendar.keys(), key=lambda day: len(calendar[day]))

    for day in sorted_days:
        events = calendar[day]
        available_slots = []

        # Find available time slots on the calendar for the current day
        if len(events) == 0:
            # If no events for the day, the whole day is available
            available_slots.append(('00:00', '23:59'))
        else:
            # Calculate available time slots between events
            for i in range(len(events) - 1):
                end_time = events[i]['endTime']
                start_time = events[i + 1]['startTime']
                available_slots.append((end_time, start_time))

        # Check if the task can be scheduled within any available time slot
        for slot in available_slots:
            slot_start = slot[0]
            slot_end = slot[1]
            slot_duration = time_difference(slot_start, slot_end)

            if slot_duration >= task_duration:
                # Check if the task can be completed before the deadline considering sleep time
                sleep_duration = time_difference(sleep_start_time, wake_up_time)
                available_duration = slot_duration - sleep_duration

                if available_duration >= task_duration:
                    # Schedule the task within the available time slot
                    task_end_time = add_time(slot_start, task_duration)
                    if time_difference(task_end_time, task_deadline) >= 0:
                        # The task can be completed before the deadline
                        return day, slot_start, task_end_time

    # If no suitable slot found, return None
    return None, None, None


def time_difference(time1, time2):
    hour1, min1 = map(int, time1.split(':'))
    hour2, min2 = map(int, time2.split(':'))
    return (hour2 - hour1) * 60 + (min2 - min1)


def add_time(time, minutes):
    hour, min = map(int, time.split(':'))
    total_minutes = hour * 60 + min + minutes
    new_hour = total_minutes // 60
    new_min = total_minutes % 60
    return f'{new_hour:02d}:{new_min:02d}'


@app.route('/')
def index():
    return render_template('index.html', calendar=calendar)

@app.route('/grocery')
def grocery():
    return render_template('grocery.html')


@app.route('/add_event', methods=['POST'])
def add_event():
    event_name = request.form['eventName']
    task_duration = int(request.form['taskDuration'])
    task_deadline = request.form['taskDeadline']
    sleep_start_time = request.form['sleepStartTime']
    wake_up_time = request.form['wakeUpTime']

    # Process the event and scheduling information here
    scheduled_day, scheduled_start_time, scheduled_end_time = schedule_task(
        event_name, task_duration, task_deadline, sleep_start_time, wake_up_time
    )

    # Add the event to the calendar if scheduled
    if scheduled_day and scheduled_start_time and scheduled_end_time:
        calendar[scheduled_day].append({
            'name': event_name,
            'startTime': scheduled_start_time,
            'endTime': scheduled_end_time
        })

    return render_template('index.html', calendar=calendar)


openai.api_key = ''

def suggest_movie(mood, genre, actors, directors, feel):
    # Generate a prompt based on user responses
    prompt = f"Based on your responses, suggest a movie that has a {mood} feel, falls under the {genre} genre, stars {actors}, directed by {directors}, and gives a {feel} vibe."

    # Generate a movie suggestion using OpenAI API
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.8
    )

    # Extract the suggested movie from the API response
    suggested_movie = response.choices[0].text.strip()

    # Return the suggested movie
    return suggested_movie


@app.route('/flix', methods=['GET', 'POST'])
def flix():
    if request.method == 'POST':
        # Retrieve user responses from the form
        mood = request.form['mood']
        genre = request.form['genre']
        actors = request.form['actors']
        directors = request.form['directors']
        feel = request.form['feel']

        # Call the function to suggest a movie based on user responses
        suggested_movie = suggest_movie(mood, genre, actors, directors, feel)

        # Render the template with the suggested movie
        return render_template('flix.html', suggested_movie=suggested_movie)

    # Render the initial form template
    return render_template('flix.html')



if __name__ == '__main__':
    app.run(debug=True)