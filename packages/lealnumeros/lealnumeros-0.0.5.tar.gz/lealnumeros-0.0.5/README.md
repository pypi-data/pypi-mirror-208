Trabalhe com formatação de números de uma maneira rápido e fácil.

```python

from lealNumeros import LealNumerosAPI

# Colocar pontuação nos números
print(LealNumerosAPI.numerosPontuados(10000))
# Saida: 10.000

# Colocar simbolos  
        # Formatos disponíveis: (8) Mil
        #                           M (Milhão)
        #                           B (Bilhão)
        #                           T (Trilhão)
        #                           Q (Quadrilhão)
        #                           Qi (Quintilhão)
        #                           Sx (Sextilhão)
        #                           Sp (Septilhão)
print(LealNumerosAPI.numerosSimbolos(10000))
# Saida: 10Mil

# Escrever o nome do número (PT-BR)
print(LealNumerosAPI.numerosNome(10000))
# Saida: Dez mil

# Escrever diferenças entre números
print(LealNumerosAPI.numerosDiferenca(10, 5))
ou
print(LealNumerosAPI.numerosDiferenca(5, 10))
# Saida: 5
```

---

Discord: silvaleal#7458
Suporte: [https://discord.gg/394ChkbKrt](https://discord.gg/394ChkbKrt)
