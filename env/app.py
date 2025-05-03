from flask import Flask, render_template, request, redirect, url_for

app= Flask(__name__)

#Example username and password
USERNAME = "Justice4julia"
PASSWORD = "1234"

@app.route("/", methods=["GET", "POST"])
def login ():
    if request.method == "POST":
        #Get the form data
        username = request.form.get("username")
        password = request.form.get("password")

        if username == USERNAME and password == PASSWORD:
            return redirect(url_for("welcome"))
        else:
            return render_template("login.html",
                                   error="invalid username or password")
    return render_template("login.html")
 
if __name__ == "main":
     app.run(debug=True)