import pytest

from src.calculator import Calculator


class TestCalculatorBasic:
    def setup_method(self):
        self.calc = Calculator()
    
    def test_add_positive_numbers(self):
        result = self.calc.add(2, 3)
        assert result == 5
    
    def test_add_negative_numbers(self):
        result = self.calc.add(-5, -3)
        assert result == -8
    
    def test_subtract_numbers(self):
        result = self.calc.subtract(10, 4)
        assert result == 6
    
    def test_multiply_numbers(self):
        result = self.calc.multiply(3, 4)
        assert result == 12
    
    def test_divide_numbers(self):
        result = self.calc.divide(10, 2)
        assert result == 5
    
    def test_divide_by_zero_raises_error(self):
        with pytest.raises(ValueError, match="Деление на ноль невозможно"):
            self.calc.divide(10, 0)
    
    def test_add_with_invalid_type_raises_error(self):
        with pytest.raises(TypeError, match="Аргументы должны быть числами"):
            self.calc.add("a", 5)


class TestCalculatorAdvanced:
    @pytest.fixture
    def calculator(self):
        return Calculator()
    
    @pytest.mark.parametrize("a,b,expected", [
        (0, 0, 0),
        (1.5, 2.5, 4.0),
        (-1, 1, 0),
        (100, -50, 50),
        (0.1, 0.2, 0.3),
    ])
    def test_add_parameterized(self, calculator, a, b, expected):
        result = calculator.add(a, b)
        if isinstance(expected, float):
            assert result == pytest.approx(expected, rel=1e-9)
        else:
            assert result == expected
    
    def test_history_after_operations(self, calculator):
        calculator.add(2, 3)
        calculator.multiply(4, 5)
        calculator.divide(10, 2)
        
        history = calculator.get_history()
        assert len(history) == 3
        assert "2 + 3 = 5" in history
        assert "4 * 5 = 20" in history
        assert "10 / 2 = 5.0" in history
    
    def test_clear_history(self, calculator):
        calculator.add(1, 2)
        calculator.subtract(5, 3)
        assert len(calculator.get_history()) == 2
        
        calculator.clear_history()
        assert len(calculator.get_history()) == 0
    
    def test_memory_operations(self, calculator):
        calculator.memory_store(42)
        assert calculator.memory_recall() == 42
        
        calculator.memory_store(3.14)
        assert calculator.memory_recall() == 3.14