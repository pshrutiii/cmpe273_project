
from flask import Flask, render_template,redirect,request,url_for,g, session,flash
from connectdb import *
from wtforms import Form,TextField,PasswordField,validators
from passlib.hash import sha256_crypt
import gc

app = Flask(__name__)

@app.route('/logout',methods = ["POST"])
def logout():
    session.pop('user',None)
    flash("YOU ARE LOGGED OUT")
    return redirect(url_for('login_page'))

@app.route('/protected')
def homepage():
    if g.user:
        return render_template("main.html")
    else:

        return redirect(url_for('login_page'))

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

@app.route('/login', methods=["GET", "POST"])
def login_page():
    error = ''
    try:

        if request.method == "POST":
            print "post req to login is sent"



            attempted_username = request.form['username']
            attempted_password = request.form['password']


            Mysql2 = Mysql()

            a = Mysql2.select('Tags', 'username = %s ', 'username', username=attempted_username)

            if a==None:
                error="Username Does not exist, please choose another"
            else:

                x = Mysql2.select('Tags', 'username = %s ', 'username', username=attempted_username)
                y = Mysql2.select('Tags', 'username = %s ', 'password', username=x)

                if attempted_username == x[0] and sha256_crypt.verify(attempted_password, y[0]):
                    print "username and password matched"
                    session['user'] = request.form['username']

                    print "session is set"
                    return redirect(url_for('homepage'))

                else:
                    error = "Invalid Password. Try Again."
                    print error
        print "get req to login is sent"
        return render_template("login.html", error=error)

    except Exception:
        return render_template("login.html", error=error)







class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


@app.route('/register', methods=["GET", "POST"])
def register_page():
    error2 = ''
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))


            Mysql2 = Mysql()
            x = Mysql2.select('Tags', 'username = %s ', 'password', username=username)



            try:
                if int(len(x)) > 0:
                    error2 = "The username is already taken, please choose another"
            except:

                Mysql2.insert("Tags", username=username, password=password, Email=email)

                print "Thanks for registering!"
                gc.collect()


                return redirect(url_for('login_page'))

        return render_template("register.html", form=form , error=error2)


    except Exception as e:
        return (str(e))

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'



    app.debug = True
    app.run()