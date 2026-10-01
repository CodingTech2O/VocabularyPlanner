from flask import Flask, jsonify, request,redirect, url_for, render_template
from forms import AddWord, UploadFileForm
import json
import os
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

with open('data/words.json', 'r') as f:
    words_data = json.load(f)

@app.route('/')
def index():
    return render_template('index.html', words=words_data)

@app.route('/add_word', methods=['GET', 'POST'])
def add_word():
    form = AddWord()
    if form.validate_on_submit():
        word = form.word.data
        meaning = form.meaning.data
        words_data[word] = meaning
        with open('data/words.json', 'w') as f:
            f.write(json.dumps(words_data))
        return redirect(url_for('index'))
    return render_template('add_word.html', form=form)

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        df = pd.read_csv(file)
        for index, row in df.iterrows():
            words_data[row['word']] = row['meaning']
        with open('data/words.json', 'w') as f:
            f.write(json.dumps(words_data))
        return redirect(url_for('index'))
    return render_template('upload_file.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)