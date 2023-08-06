import pytest
from .imc import calcular_imc


def test_imc():
    imc = calcular_imc(70, 1.75)
    assert imc == 22.86


def test_imc_zero_division():
    with pytest.raises(ZeroDivisionError):
        calcular_imc(70, 0)
