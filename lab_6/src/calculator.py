class Calculator:
    def __init__(self):
        self.history = []
        self.memory = 0
    
    def add(self, a: float, b: float) -> float:
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Аргументы должны быть числами")
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a: float, b: float) -> float:
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Аргументы должны быть числами")
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a: float, b: float) -> float:
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Аргументы должны быть числами")
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a: float, b: float) -> float:
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Аргументы должны быть числами")
        if b == 0:
            raise ValueError("Деление на ноль невозможно")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result
    
    def clear_history(self):
        self.history.clear()
    
    def get_history(self) -> list:
        return self.history.copy()
    
    def memory_store(self, value: float):
        self.memory = value
    
    def memory_recall(self) -> float:
        return self.memory