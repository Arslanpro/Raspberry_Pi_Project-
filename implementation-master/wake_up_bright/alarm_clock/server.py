from wake_up_bright.alarm_clock.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)