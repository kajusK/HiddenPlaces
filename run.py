from app import create_app, database

app = create_app()
database.db.create_all(app=app)

if __name__ == '__main__':
    app.run(debug=True)
