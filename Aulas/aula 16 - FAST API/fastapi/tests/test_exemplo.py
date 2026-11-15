# FUNCAO a ser testada (exemplo do slide)
def somar(a, b):
    return a + b


# TEST - a função retorna o valor esperado
def test_somar():
    resultado = somar(2, 3)   # Act
    assert resultado == 5     # Assert


# TEST - exemplo mais simples possível de assert
def test_exemplo():
    assert 1 + 1 == 2
