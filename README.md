# hylas
Webapp for visualizing ML'd data

## Requirements

* [Python 2.7.x](https://www.python.org/)
* [Flask](http://flask.pocoo.org/)
* [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.1/)
* [Flask-Security](https://pythonhosted.org/Flask-Security/)
* [Numpy](http://www.numpy.org/)
* [Scikit-Learn](http://scikit-learn.org/stable/)
* [DSSG Diogenes](https://github.com/dssg/diogenes)
* [Bower](http://bower.io/)
* [wkhtmltopdf](http://wkhtmltopdf.org/)

## Running

1. Install required dependencies.
2. From the project's root directory, run `bower install`.
3. If you are running on a headless server, you will have to 
   [configure wkhtmltopdf to run without X](https://github.com/JazzCore/python-pdfkit/wiki/Using-wkhtmltopdf-without-X-server)
3. Create a `config.py` file in the project's root directory. You may use the 
   included `config.py.sample` as a template.
4. Run `python server.py` to start the server
5. Visit `http://127.0.0.1:5000/` with a web browser. This creates the user
   database.
6. Terminate the server.
7. Run `python add_user.py USERNAME PASSWORD` to add a user to the database.
8. Start the server again with `python server.py`. 
9. Visit `http://127.0.0.1:5000/` and log in with the username and password you    have just created.
