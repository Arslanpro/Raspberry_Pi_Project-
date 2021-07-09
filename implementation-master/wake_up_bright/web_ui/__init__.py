from wake_up_bright.web_ui.web_app import create_app

app = create_app()

if __name__ == "__main__":
    # TODO: Add a way to include a .flaskenv file and .env file for environment variables
    # app.run()
    app.run(host='0.0.0.0', port=8080, debug=True, load_dotenv=True)
