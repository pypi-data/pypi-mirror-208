from wtforms import StringField, PasswordField, validators, DateField
from trexadmin.forms.base_forms import ValidationBaseForm
from trexadmin.libs.wtforms import validators as custom_validator
from flask_babel import gettext
from datetime import date

class UserMinForm(ValidationBaseForm):
    name                = StringField(gettext('Name'), validators=[
                                        validators.InputRequired(gettext('Name is required')),
                                        validators.Length(min=3, max=300, message='Name length must be within 3 and 300 characters'),
                                        
                                        ]
                                        )
    mobile_phone        = StringField('Mobile Phone', validators=[
                                        #validators.InputRequired(gettext('Mobile Phone is required')),
                                        ]
                                        )
    
    gender              = StringField('Gender', validators=[
                                        validators.InputRequired(gettext('Gender is required')),
                                        ]
                                        )
    
    birth_date          = StringField('Mobile Phone', validators=[
                                        validators.InputRequired(gettext('Birth date is required')),
                                        ]
                                        )
    
    
    
class UserRegistrationForm(UserMinForm):
    email               = StringField('Email Address', validators=[
                                        validators.Email(gettext("Please enter valid email address.")),
                                        validators.InputRequired(gettext('Email is required')),
                                        ]
                                        )
    
    password            = StringField(gettext('Password'), validators=[
                                        validators.InputRequired(gettext('Password is required')),
                                        
                                        ]
                                        )  
    
class UserUpdateForm(UserMinForm):
    reference_code      = StringField('User Reference Code', validators=[
                                        validators.InputRequired(gettext('User Reference Code is required')),
                                        ]
                                        )      
    
  