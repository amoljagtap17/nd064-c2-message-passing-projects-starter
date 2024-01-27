import os

from app import create_app, run_consumer

app = create_app(os.getenv("FLASK_ENV") or "test")

if __name__ == "__main__":
    run_consumer()
    app.run(debug=True)
