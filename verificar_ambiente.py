import sys

print("--- Verificador de Ambiente Virtual ---")
print("Este script está sendo executado pelo seguinte interpretador Python:")
print(sys.executable)

if 'ambiente_grafos' in sys.executable:
    print("\n✅ CONFIRMADO: O script está rodando de dentro do ambiente virtual 'ambiente_grafos'.")
else:
    print("\n⚠️ ATENÇÃO: O script NÃO parece estar rodando do ambiente virtual esperado.")