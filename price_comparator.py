from flask import Flask
from flask import render_template

app = Flask(__name__)

###################################
# Google API key.
MAPS_KEY = 'AIzaSyCs7YDHV5QF2QgJt8aJ1cKvFfxrIwSjsN0'
JS_API_KEY = 'AIzaSyBYXFWRwOAPQ03YrXRDfLheFkeV2nc0sAk'
###################################

@app.route("/")
def price_comparator():
    global JS_API_KEY
    return render_template('price_comparator.html', maps_key=JS_API_KEY)

if __name__ == "__main__":
    app.run()
