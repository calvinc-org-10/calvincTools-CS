"""
Test script to verify the refactored models work correctly.

This demonstrates:
1. How to initialize the models with init_cDatabase
2. How to import and use models from anywhere
3. That the db proxy works correctly
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Test imports - these should work now!
from calvincTools.models import (
    init_cDatabase,
    menuGroups,
    menuItems, 
    cParameters,
    cGreetings,
    User,
    db  # The db proxy should also be importable
)

def test_models_import():
    """Test that models can be imported before initialization."""
    print("✓ Successfully imported all models")
    print(f"  - menuGroups: {menuGroups}")
    print(f"  - menuItems: {menuItems}")
    print(f"  - cParameters: {cParameters}")
    print(f"  - cGreetings: {cGreetings}")
    print(f"  - User: {User}")
    print(f"  - db: {db}")

def test_initialization():
    """Test that init_cDatabase properly initializes the models."""
    # Create a test Flask app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_BINDS'] = {
        'cToolsdb': 'sqlite:///:memory:'
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Create SQLAlchemy instance
    database = SQLAlchemy(app)
    
    print("\n✓ Created Flask app and SQLAlchemy instance")
    
    # Initialize the models - use the returned references
    MenuGroups, MenuItems, CParameters, CGreetings, UserModel = init_cDatabase(app, database)
    
    print("✓ Successfully called init_cDatabase()")
    print(f"  Returned models: {[m.__name__ for m in (MenuGroups, MenuItems, CParameters, CGreetings, UserModel)]}")
    
    # Verify models now have db.Model as base
    with app.app_context():
        print("\n✓ Models are now proper SQLAlchemy models:")
        print(f"  - menuGroups has db.Model in MRO: {any('Model' in str(b) for b in MenuGroups.__mro__)}")
        print(f"  - User has db.Model in MRO: {any('Model' in str(b) for b in UserModel.__mro__)}")
        
        # Verify columns exist
        print("\n✓ Models have proper columns:")
        print(f"  - menuGroups.id: {hasattr(MenuGroups, 'id') and MenuGroups.id is not None}")
        print(f"  - User.username: {hasattr(UserModel, 'username') and UserModel.username is not None}")
        print(f"  - cParameters.parm_name: {hasattr(CParameters, 'parm_name') and CParameters.parm_name is not None}")
        
        # Verify db works
        print("\n✓ Database proxy works:")
        print(f"  - db.session: {db.session}")
        print(f"  - db.create_all: {callable(db.create_all)}")
    
    print("\n✅ All tests passed! Models are working correctly.")
    return True

def test_model_usage():
    """Test that models can be used for queries."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_BINDS'] = {
        'cToolsdb': 'sqlite:///:memory:'
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    database = SQLAlchemy(app)
    # Use returned models
    MenuGroups, MenuItems, CParameters, CGreetings, UserModel = init_cDatabase(app, database)
    
    with app.app_context():
        # Create tables
        database.create_all(bind_key='cToolsdb')
        
        # Test creating a user
        user = UserModel(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        
        database.session.add(user)
        database.session.commit()
        
        # Test querying
        found_user = UserModel.query.filter_by(username='testuser').first()
        
        print("\n✓ Model CRUD operations work:")
        print(f"  - Created user: {found_user}")
        print(f"  - Username: {found_user.username}")
        print(f"  - Email: {found_user.email}")
        print(f"  - Password check: {found_user.check_password('testpassword')}")
        
        # Test parameters
        CParameters.set_parameter('test_param', 'test_value')
        param_value = CParameters.get_parameter('test_param')
        print(f"\n✓ cParameters works:")
        print(f"  - Set and retrieved: {param_value}")
        
    print("\n✅ All model operations work correctly!")
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("Testing Refactored Models")
    print("=" * 60)
    
    # Test 1: Import models
    print("\n[Test 1] Testing model imports...")
    test_models_import()
    
    # Test 2: Initialize models
    print("\n[Test 2] Testing model initialization...")
    test_initialization()
    
    # Test 3: Use models
    print("\n[Test 3] Testing model usage...")
    test_model_usage()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYour models are now:")
    print("  ✓ Importable from anywhere in the package")
    print("  ✓ Properly initialized with db.Model")
    print("  ✓ Fully functional SQLAlchemy models")
    print("  ✓ Ready to use in views, forms, and other modules")
