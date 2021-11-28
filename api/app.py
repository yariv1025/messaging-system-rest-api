from api import create_app

app = create_app()

if __name__ == '__main__':
    # app running configuration already set up in create_app()
    app.run()
