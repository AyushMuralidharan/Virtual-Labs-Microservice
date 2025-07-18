import requests
import webbrowser
import tempfile
import os

# Sample Python code to analyze
sample_code = """
class Vehicle:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

    def start_engine(self):
        return f"{self.brand} {self.model}'s engine is starting"

class Car(Vehicle):
    def __init__(self, brand, model, doors):
        super().__init__(brand, model)
        self.doors = doors

    def honk(self):
        return "Beep beep!"

class Motorcycle(Vehicle):
    def __init__(self, brand, model, has_sidecar):
        super().__init__(brand, model)
        self.has_sidecar = has_sidecar

    def wheelie(self):
        return "Performing a wheelie!"

class ElectricCar(Car):
    def __init__(self, brand, model, doors, battery_capacity):
        super().__init__(brand, model, doors)
        self.battery_capacity = battery_capacity

    def charge(self):
        return f"Charging {self.battery_capacity}kWh battery"
"""

def test_visualization(model_type):
    print(f"\nTesting {model_type} visualization...")
    response = requests.post(
        "http://localhost:8000/analyze",
        json={
            "code": sample_code,
            "target_architecture": model_type
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('visualization'):
            # Create a temporary HTML file and open it in the browser
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
                f.write(data['visualization'])
                temp_path = f.name
            
            print(f"Opening {model_type} visualization in browser...")
            webbrowser.open('file://' + temp_path)
            
            # Wait for user input before deleting the file
            input("Press Enter to continue...")
            os.unlink(temp_path)
        else:
            print("No visualization data received")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Test all visualizations
    for model_type in ["uml", "4+1", "adl"]:
        test_visualization(model_type) 