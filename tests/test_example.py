import pytest


class Student:
    def __init__(self, first_name: str, last_name: str, age: int, grade: int):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.grade = grade


@pytest.fixture
def default_student():
    return Student("Khashayar", "Sabzevari", 37, 100)


def test_student(default_student):
    assert default_student.first_name == "Khashayar", "First name should be Khashayar"
