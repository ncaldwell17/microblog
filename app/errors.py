from flask import render_template
from app import app, db

# error functions work similarly to view functions 

# each of these return a second value, the error code no. 

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    # rolls back the database to check input 
    db.session.rollback()
    return render_template('500.html'), 500