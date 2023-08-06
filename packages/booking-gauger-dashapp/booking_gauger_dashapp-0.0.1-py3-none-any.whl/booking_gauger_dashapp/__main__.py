from booking_gauger_dashapp.app import app

if __name__ == '__main__':
    app.run_server(port='4048', host='0.0.0.0', debug=False, use_reloader=False)