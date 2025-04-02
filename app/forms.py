from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, URL, Optional
from app.models import User

class LoginForm(FlaskForm):
    """Form for user login"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """Form for user registration"""
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        """Validate that the username is not already taken"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        """Validate that the email is not already registered"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')

class ResetPasswordRequestForm(FlaskForm):
    """Form for requesting a password reset"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    """Form for resetting password"""
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password',
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class ProfileUpdateForm(FlaskForm):
    """Form for updating user profile"""
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[Length(max=64)])
    last_name = StringField('Last Name', validators=[Length(max=64)])
    bio = TextAreaField('Bio')
    submit = SubmitField('Update Profile')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        """Validate that the username is not already taken"""
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        """Validate that the email is not already registered"""
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already registered. Please use a different one.')

class PageForm(FlaskForm):
    """Form for creating and editing pages"""
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=100)])
    slug = StringField('Slug', validators=[DataRequired(), Length(min=3, max=100)])
    summary = TextAreaField('Summary', validators=[Optional(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    featured_image = FileField('Featured Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    is_published = BooleanField('Publish')
    tags = SelectMultipleField('Tags', coerce=int)
    submit = SubmitField('Save')

class MediaUploadForm(FlaskForm):
    """Form for uploading media files"""
    file = FileField('File', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'pdf', 'doc', 'docx'], 'Supported file types only!')])
    file_type = SelectField('File Type', choices=[('image', 'Image'), ('document', 'Document')])
    alt_text = StringField('Alt Text', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Upload')

class TagForm(FlaskForm):
    """Form for creating and editing tags"""
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Save')
