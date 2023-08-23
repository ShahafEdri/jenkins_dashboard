import time
from flask import Flask, render_template, request
import pandas as pd
from job_manager import JobManager
from dashboard import Dashboard



app = Flask(__name__)

job_manager = JobManager()
dashboard = Dashboard()


@app.route('/list')
def get_list():
    jobs_data = job_manager.get_all_jobs_data()
    df = dashboard.format_data_to_df(jobs_data)

    return render_template('index.html', job_df=df.to_html(index=False))


@app.route('/execute', methods=['POST'])
def execute_command():
    command = request.form['command']
    jobs_data = job_manager.get_all_jobs_data()
    df = dashboard.format_data_to_df(jobs_data)

    # Process the command as needed (e.g., send it to the backend)
    # ...


    # Simulating command execution and getting success status
    time.sleep(3)  # Simulating some processing time
    success = True  # Replace with your actual command execution logic
    
    if success:
        response = 'Command succeeded: ' + command
    else:
        response = 'Command failed: ' + command
    
    return render_template('index.html', response=response, job_df=df.to_html(index=False))


if __name__ == '__main__':
    app.run(debug=True)
