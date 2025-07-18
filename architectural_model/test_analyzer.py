import requests
import json

# Sample Python code to analyze
sample_code = """
class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def bark(self):
        return "Woof!"

class Cat(Animal):
    def meow(self):
        return "Meow!"
"""

def test_uml_conversion():
    print("Testing UML conversion...")
    response = requests.post(
        "http://localhost:8000/analyze",
        json={
            "code": sample_code,
            "target_architecture": "uml"
        }
    )
    print("UML Response:")
    print(json.dumps(response.json(), indent=2))

def test_4plus1_conversion():
    print("\nTesting 4+1 View Model conversion...")
    response = requests.post(
        "http://localhost:8000/analyze",
        json={
            "code": sample_code,
            "target_architecture": "4+1"
        }
    )
    print("4+1 View Model Response:")
    print(json.dumps(response.json(), indent=2))

def test_adl_conversion():
    print("\nTesting ADL conversion...")
    response = requests.post(
        "http://localhost:8000/analyze",
        json={
            "code": sample_code,
            "target_architecture": "adl"
        }
    )
    print("ADL Response:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    # Test all conversions
    test_uml_conversion()
    test_4plus1_conversion()
    test_adl_conversion() 