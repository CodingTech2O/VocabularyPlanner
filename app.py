from flask import Flask, jsonify, request, redirect, url_for, render_template, flash
from forms import AddWord, UploadFileForm
from dotenv import load_dotenv
import json
import os
import random
import pandas as pd

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

WORDS_FILE = 'data/words.json'
REVISE_FILE = 'data/revise.json'


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


words_data = load_json(WORDS_FILE, {})

# Words still to be revised. Starts as every word; swiping right removes a word.
revise_list = load_json(REVISE_FILE, None)
if revise_list is None:
    revise_list = list(words_data.keys())
    save_json(REVISE_FILE, revise_list)


def add_words(new_words):
    for word, meaning in new_words.items():
        words_data[word] = meaning
        if word not in revise_list:
            revise_list.append(word)
    save_json(WORDS_FILE, words_data)
    save_json(REVISE_FILE, revise_list)


@app.route('/')
def index():
    return render_template('index.html', words=words_data, revise_count=len(revise_list))


@app.route('/add_word', methods=['GET', 'POST'])
def add_word():
    form = AddWord()
    if form.validate_on_submit():
        word = form.word.data.strip()
        meaning = form.meaning.data.strip()
        if word and meaning:
            add_words({word: meaning})
            flash(f'Added "{word}"')
            return redirect(url_for('index'))
        flash('Both word and meaning are required')
    return render_template('add_word.html', form=form)


@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        df = pd.read_csv(file).dropna(subset=['word', 'meaning'])
        new_words = {str(row['word']).strip(): str(row['meaning']).strip() for _, row in df.iterrows()}
        add_words(new_words)
        flash(f'Uploaded {len(new_words)} words')
        return redirect(url_for('index'))
    return render_template('upload_file.html', form=form)


@app.route('/revise')
def revise():
    cards = [{'word': w, 'meaning': words_data[w]} for w in revise_list if w in words_data]
    random.shuffle(cards)
    return render_template('revise.html', cards=cards, total_words=len(words_data))


@app.route('/revise/answer', methods=['POST'])
def revise_answer():
    payload = request.get_json(silent=True) or {}
    word = payload.get('word')
    known = payload.get('known')
    if word not in words_data or not isinstance(known, bool):
        return jsonify({'error': 'invalid request'}), 400

    if known:
        if word in revise_list:
            revise_list.remove(word)
    elif word not in revise_list:
        revise_list.append(word)
    save_json(REVISE_FILE, revise_list)
    return jsonify({'remaining': len(revise_list)})


@app.route('/revise/reset', methods=['POST'])
def revise_reset():
    revise_list[:] = list(words_data.keys())
    save_json(REVISE_FILE, revise_list)
    flash('All words added back to the revision list')
    return redirect(url_for('revise'))


if __name__ == '__main__':
    app.run(debug=True)
