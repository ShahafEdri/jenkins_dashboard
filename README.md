# jenkins-dashboard

A simple command-line tool for displaying a dashboard of the current Jenkins runs. This tool uses the Jenkins API to fetch data about running jobs and their status, and displays the data in a tabular format in the terminal.

The tool supports authentication with a Jenkins token, and caches API responses to avoid unnecessary requests. It also allows the user to specify a refresh interval for automatic updates of the dashboard.

This project is written in Python and uses the requests library for making HTTP requests to the Jenkins API.
