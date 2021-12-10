from flask import Flask, render_template
import revive

web_site = Flask(__name__)

@web_site.route('/')
def index():
    revive.set_up()
    return render_template('index.html')

web_site.run(host='0.0.0.0', port=8080)