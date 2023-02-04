from apps.authentication.user_model import User

def test_new_user():
    """
    GIVEN a User Model
    WHEN a new User is created
    THEN check the user
    """
    user = User('201910449','Jekujeku','echoquintanilla@gmail.com','Analytico@0322')
    assert user.employee_id == '201910449'
    assert user.username == 'Jekujeku'
    assert user.email == 'echoquintanilla@gmail.com'
    assert user.password_hashed != 'Analytico@0322'
