
from flask import Flask, render_template,redirect,request,url_for,g,flash, session
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


@app.route('/login', methods=["GET", "POST"])
def login_page():
    error = ''
    try:

        if request.method == "POST":

            attempted_username = request.form['username']
            attempted_password = request.form['password']


            Mysql2 = Mysql()

            a = Mysql2.select('user_table', 'login_id = %s ', 'login_id', username=attempted_username)

            if a == None:
                flash("Username Does not exist")
            else:

                x = Mysql2.select('user_table', 'login_id = %s ', 'login_id', login_id=attempted_username)
                y = Mysql2.select('user_table', 'login_id = %s ', 'password', login_id=x)

                if attempted_username == x[0] and sha256_crypt.verify(attempted_password, y[0]):
                    session['user'] = request.form['username']
                    print "session is set"

                    return redirect(url_for('homepage'))

                else:
                    flash("Invalid Password. Try Again.")
        return render_template("login.html", error=error)

    except Exception:
        return render_template("login.html", error=error)



@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']



class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


@app.route('/register', methods=["GET", "POST"])
def register_page():
    error=''
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username = form.username.data
            password = sha256_crypt.encrypt((str(form.password.data)))


            Mysql2 = Mysql()
            x = Mysql2.select('user_table', 'login_id = %s ', 'password', username=username)



            try:
                if int(len(x)) > 0:
                    flash("username already taken")
            except:

                 if(Mysql2.insert("user_table", login_id=username, password=password)):
                    gc.collect()


                 session['user']=username

                 return redirect(url_for('homepage'))


        return render_template("register.html", form=form )


    except Exception as e:
        return (str(e))




@app.route('/', methods =['GET', 'POST'])
def homepage():
    if g.user:

        return render_template("main.html")
    else:
        flash("YOU NEED TO LOGIN")

        return redirect(url_for('login_page'))




if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'



    app.debug = True
    app.run()