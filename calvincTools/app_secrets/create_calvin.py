########################################
########################################
########################################

def create_calvin(app,
    username="calvinc460",
    eml = "cdev@notreal.mail",
    pw = "WyrdPass",
    mGroup = 1
    ):
    from ..models import User, db

    # Create new user
    Calvin_DA_MAN = User(
        username=username,
        first_name="Calvin",
        last_name="C",
        email=eml,
        password_optional=True,
        is_superuser=True,
        menuGroup=mGroup,
        )      # type: ignore
    Calvin_DA_MAN.set_password(pw)

    with app.app_context():
        if User.query.filter_by(username=username).first():
            db.session.rollback()
            print(f"User '{username}' already exists. No new user created.")
            return

        db.session.add(Calvin_DA_MAN)
        db.session.commit()
        print(f"User '{username}' created successfully.")
    # end with app.app_context()
# create_calvin

