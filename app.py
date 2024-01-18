from flask import Flask, render_template, request, redirect, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from uuid import uuid4

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

class File(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    filename = db.Column(db.String(200), nullable = False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    files = File.query.all()
    return render_template("index.html", files = files)

@app.route('/uploads', methods=['POsT'])
def uploads():
    if request.method == "POST":
        print('Upload Image')
        file = request.files['file']
        if file:
            filename = file.filename.split('.')[-2] + str(uuid4()) + "." + file.filename.split('.')[-1]
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_file = File(filename= filename)
            db.session.add(new_file)
            db.session.commit()
            return redirect('/')
    return 'something went wrong, please try again'

@app.route('/uploaded_file/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/download/<int:file_id>')
def download(file_id):
    file = File.query.get_or_404(file_id)
    return send_from_directory(app.config['UPLOAD_FOLDER'], file.filename, as_attachment = True)

@app.route('/delete/<int:file_id>')
def delete(file_id):
    file = File.query.get_or_404(file_id)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    os.remove(file_path)
    db.session.delete(file)
    db.session.commit()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)