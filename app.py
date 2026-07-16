from flask import Flask, render_template

from services.dashboard_service import get_dashboard_data

app = Flask(__name__)


@app.route("/")
def home():
    dashboard = get_dashboard_data()
    return render_template("index.html", dashboard=dashboard)


if __name__ == "__main__":
    app.run(debug=True)