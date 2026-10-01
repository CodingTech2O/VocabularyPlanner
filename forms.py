from wtforms import StringField, SubmitField,FileField
from flask_wtf import FlaskForm

class AddWord(FlaskForm):
    word = StringField('Word')
    meaning = StringField('Meaning')
    submit = SubmitField('Add Word')

class UploadFileForm(FlaskForm):
    file = FileField('File - Format: .csv, Content: word, meaning')
    submit = SubmitField('Upload File')