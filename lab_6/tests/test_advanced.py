import pytest

from unittest.mock import MagicMock, patch
from src.calculator import Calculator


class TestCalculatorMocking:
    def test_history_with_mock(self):
        calculator = Calculator()
        
        mock_history = MagicMock()
        calculator.history = mock_history
        
        calculator.add(2, 3)
        
        mock_history.append.assert_called_once_with("2 + 3 = 5")
    
    @patch('src.calculator.Calculator.add')
    def test_chained_operations_with_stub(self, mock_add):
        calculator = Calculator()
        
        mock_add.return_value = 10
        
        result1 = calculator.add(2, 3)
        result2 = calculator.multiply(result1, 4)
        
        assert result1 == 10
        assert result2 == 40
        mock_add.assert_called_once_with(2, 3)
    
    @pytest.mark.parametrize("operation,args,expected", [
        ("add", (2, 3), 5),
        ("subtract", (10, 4), 6),
        ("multiply", (3, 4), 12),
        ("divide", (10, 2), 5),
    ])
    def test_all_operations_parameterized(self, operation, args, expected):
        calculator = Calculator()
        
        method = getattr(calculator, operation)
        result = method(*args)
        
        assert result == expected
    
    def test_concurrent_operations_independence(self):
        calc1 = Calculator()
        calc2 = Calculator()
        
        calc1.add(1, 2)
        calc2.multiply(3, 4)
        
        assert len(calc1.get_history()) == 1
        assert len(calc2.get_history()) == 1
        assert "1 + 2 = 3" in calc1.get_history()
        assert "3 * 4 = 12" in calc2.get_history()