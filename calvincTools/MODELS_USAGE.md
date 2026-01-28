# Example: How to use the refactored models

## Overview

The models (menuGroups, User, menuItems, cParameters, cGreetings) are now defined at the module level and can be imported directly in any file within the package.

## How it works

1. **Models are defined as placeholder classes** in `models.py` at the module level
2. **`init_cDatabase()` function** converts them to proper SQLAlchemy models
3. **After initialization**, the models work normally and can be imported anywhere

## Usage Pattern

### In your main app file (e.g., app.py or __init__.py):

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Import the initialization function
from calvincTools.models import init_cDatabase

# Create Flask app and SQLAlchemy instance
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SQLALCHEMY_BINDS'] = {
    'cToolsdb': 'sqlite:///ctools.db'
}

db = SQLAlchemy(app)

# Initialize the database models
# This MUST be called before using any models
init_cDatabase(app, db)

# Now the models are ready to use!
```

**Note**: If you import models before calling `init_cDatabase()` and then call it, you should either:
1. Use the returned model references from `init_cDatabase()`, OR
2. Re-import the models after initialization, OR  
3. Import models in other modules (they will automatically get the initialized versions)

```python
# Option 1: Use returned references
menuGroups, menuItems, cParameters, cGreetings, User = init_cDatabase(app, db)

# Option 2: Re-import after init
init_cDatabase(app, db)
from calvincTools.models import menuGroups, User  # These will be the initialized versions

# Option 3: Import in other modules (recommended)
# Other modules that import AFTER init_cDatabase() will get the right versions automatically
```

### In other modules (views, forms, etc.):

```python
# In calvincTools/cMenu/views.py
from ..models import menuItems, menuGroups

def get_menu():
    # Use the models normally
    groups = menuGroups.query.all()
    items = menuItems.query.filter_by(MenuID=0).all()
    return groups, items
```

```python
# In calvincTools/forms.py
from .models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if not user:
            raise ValidationError('User not found')
```

```python
# In calvincTools/usr_auth/views.py
from ..models import User

@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(request.form['password']):
        login_user(user)
        return redirect(url_for('menu.index'))
```

```python
# In calvincTools/views/util_views.py
from ..models import cParameters, cGreetings

def get_app_config():
    greeting = cGreetings.query.first()
    app_name = cParameters.get_parameter('app_name', default='Calvin Tools')
    return {'greeting': greeting, 'app_name': app_name}
```

## Key Points

1. **Import works normally**: `from .models import User, menuGroups, menuItems`
2. **Call `init_cDatabase()` first**: Must be called in your main app before using models
3. **Models are visible everywhere**: After initialization, all modules can import and use them
4. **No circular imports**: The models module doesn't depend on your app structure
5. **Type hints work**: IDEs and type checkers will show some warnings on the placeholder classes, but the actual models work correctly at runtime

## Database Access

The `db` object is also available via a proxy:

```python
from calvincTools.models import db

# Use db session
db.session.add(new_user)
db.session.commit()

# Create all tables
db.create_all()
```

## Migration from Old Code

If you have existing code that was trying to import models:

**Before** (wouldn't work):
```python
from ..models import menuGroups  # Error: inside init_cDatabase function
```

**After** (works!):
```python
from ..models import menuGroups  # Success: module-level class
# Use menuGroups normally
group = menuGroups.query.filter_by(GroupName="Main").first()
```

No changes needed to your import statements - they will just start working!
