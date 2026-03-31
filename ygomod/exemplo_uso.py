#!/usr/bin/env python3
"""
Exemplo de uso da ferramenta Forbidden Memories Modifier

Este script demonstra como modificar cartas e adicionar efeitos
de forma programática.
"""

from fm_modifier import (
    ForbiddenMemoriesROM, 
    CardData, 
    EFFECT_FLAGS,
    ATTRIBUTES,
    CARD_TYPES
)


def exemplo_basico():
    """Exemplo básico de modificação de carta"""
    print("=" * 60)
    print("EXEMPLO 1: Modificação Básica de Carta")
    print("=" * 60)
    
    # Criar uma carta de exemplo
    carta = CardData(
        card_id=123,
        name="Dragão Branco",
        attack=3000,
        defense=2500,
        level=8,
        attribute=0x04,  # Light
        type_=0x01,      # Monstro Efeito
        effect_flags=0
    )
    
    print(f"\nCarta original:")
    print(f"  ID: {carta.card_id}")
    print(f"  Nome: {carta.name}")
    print(f"  ATK: {carta.attack}, DEF: {carta.defense}")
    print(f"  Level: {carta.level}")
    print(f"  Atributo: {carta.get_attribute_name()}")
    print(f"  Tipo: {carta.get_type_name()}")
    print(f"  Efeitos: {carta.get_effects_list() or 'Nenhum'}")
    
    # Adicionar efeitos
    print("\nAdicionando efeitos...")
    carta.add_effect(0x0001)  # Não pode ser destruído em batalha
    carta.add_effect(0x0010)  # Imune a magias
    
    print(f"\nCarta modificada:")
    print(f"  Efeitos: {carta.get_effects_list()}")
    
    # Converter para bytes (como seria gravado na ROM)
    dados_binarios = carta.to_bytes()
    print(f"\nDados binários (hex): {dados_binarios.hex().upper()}")
    print(f"Tamanho: {len(dados_binarios)} bytes")


def exemplo_efeitos():
    """Exemplo mostrando todos os efeitos disponíveis"""
    print("\n" + "=" * 60)
    print("EXEMPLO 2: Lista de Efeitos Disponíveis")
    print("=" * 60)
    
    print("\nEfeitos que podem ser aplicados às cartas:\n")
    
    for codigo, descricao in EFFECT_FLAGS.items():
        print(f"  0x{codigo:04X} - {descricao}")
    
    # Exemplo de combinação de efeitos
    print("\n\nExemplo de combinações populares:")
    
    # Carta "quase invencível"
    combo_invencivel = 0x0001 | 0x0010 | 0x0020  # Não destruído + Imune magia + Imune armadilha
    print(f"\n  Combo 'Tanque': 0x{combo_invencivel:04X}")
    print(f"    - Não pode ser destruído em batalha")
    print(f"    - Imune a magias")
    print(f"    - Imune a armadilhas")
    
    # Carta de ataque rápido
    combo_rapido = 0x0004 | 0x0008  # Ataque direto + Ataca duas vezes
    print(f"\n  Combo 'Ataque Rápido': 0x{combo_rapido:04X}")
    print(f"    - Ataque direto permitido")
    print(f"    - Pode atacar duas vezes")
    
    # Carta de controle
    combo_controle = 0x0800 | 0x2000  # Negate efeitos + Pesca de carta
    print(f"\n  Combo 'Controle': 0x{combo_controle:04X}")
    print(f"    - Negate efeitos")
    print(f"    - Pesca de carta")


def exemplo_rom_simulation():
    """Simula o processo de modificação de ROM"""
    print("\n" + "=" * 60)
    print("EXEMPLO 3: Simulação de Modificação de ROM")
    print("=" * 60)
    
    # Simular carregamento de ROM (cria dados fictícios)
    print("\n1. Carregando ROM...")
    rom_data = bytearray(1024)  # ROM fictícia de 1KB
    
    # Colocar uma carta no offset 0x100
    carta_original = CardData(
        card_id=50,
        name="Mago Negro",
        attack=2500,
        defense=2100,
        level=7,
        attribute=0x01,  # Dark
        type_=0x01,
        effect_flags=0
    )
    
    # Escrever carta na ROM simulada
    offset = 0x100
    rom_data[offset:offset+11] = carta_original.to_bytes()
    print(f"   Carta original no offset 0x{offset:X}")
    print(f"   ATK={carta_original.attack}, DEF={carta_original.defense}")
    
    # Modificar ATK/DEF
    print("\n2. Modificando ATK/DEF...")
    novo_atk = 2800
    nova_def = 2400
    rom_data[offset+2:offset+4] = novo_atk.to_bytes(2, 'little')
    rom_data[offset+4:offset+6] = nova_def.to_bytes(2, 'little')
    print(f"   Novo ATK={novo_atk}, DEF={nova_def}")
    
    # Adicionar efeito
    print("\n3. Adicionando efeito...")
    efeito_flag = 0x0010  # Imune a magias
    flags_atuais = int.from_bytes(rom_data[offset+9:offset+11], 'little')
    novas_flags = flags_atuais | efeito_flag
    rom_data[offset+9:offset+11] = novas_flags.to_bytes(2, 'little')
    print(f"   Efeito adicionado: Imune a magias (0x0010)")
    
    # Ler carta modificada
    print("\n4. Lendo carta modificada...")
    carta_modificada = CardData.from_bytes(rom_data[offset:offset+11])
    print(f"   ATK={carta_modificada.attack}, DEF={carta_modificada.defense}")
    print(f"   Efeitos: {carta_modificada.get_effects_list()}")


def exemplo_busca_carta():
    """Exemplo de busca de carta por ID"""
    print("\n" + "=" * 60)
    print("EXEMPLO 4: Busca e Visualização de Cartas")
    print("=" * 60)
    
    # Mostrar IDs de algumas cartas famosas (exemplo)
    cartas_famosas = {
        1: "Dragão Branco de Olhos Azuis",
        2: "Mago Negro",
        3: "Gaia The Fierce Knight",
        4: "Kuriboh",
        5: "Summoned Skull"
    }
    
    print("\nIDs de exemplo de cartas famosas:")
    for id_carta, nome in cartas_famosas.items():
        print(f"  ID {id_carta}: {nome}")
    
    print("\nPara usar na ferramenta:")
    print("  1. Carregue sua ROM")
    print("  2. Use a opção 6 para ver informações de uma carta")
    print("  3. Digite o ID da carta desejada")
    print("  4. Veja ATK, DEF, Level, Atributo, Tipo e Efeitos")


def dicas_engenharia_reversa():
    """Dicas para encontrar offsets reais"""
    print("\n" + "=" * 60)
    print("DICAS DE ENGENHARIA REVERSA")
    print("=" * 60)
    
    print("""
Para encontrar os offsets corretos dos dados das cartas na ROM:

1. MÉTODO DA BUSCA HEXADECIMAL:
   - Abra a ROM em um editor hexadecimal (HxD, Hex Fiend)
   - Procure por valores conhecidos (ex: ATK 3000 = 0x0BB8)
   - Dragão Branco tem ATK 3000 e DEF 2500
   - Busque pela sequência: BB 0B C8 09 (3000, 2500 em little-endian)

2. MÉTODO DO EMULADOR COM DEBUGGER:
   - Use DuckStation ou ePSXE com plugin de debug
   - Monitore acessos à memória durante duelos
   - Identifique onde os dados das cartas são lidos

3. FERRAMENTAS RECOMENDADAS:
   - HxD Editor (Windows)
   - Hex Fiend (macOS)
   - Ghidra (análise estática)
   - DuckStation (emulador com debugger)

4. VERSÕES DIFERENTES:
   - NTSC-U (EUA): Offsets podem diferir de PAL (Europa)
   - Sempre teste em múltiplas versões

5. BACKUP SEMPRE!
   - Faça cópia da ROM original antes de modificar
   - Trabalhe em cima da cópia
""")


if __name__ == "__main__":
    print("\n" + "🃏" * 30)
    print("YU-GI-OH! FORBIDDEN MEMORIES MODIFIER")
    print("Exemplos de Uso")
    print("🃏" * 30)
    
    exemplo_basico()
    exemplo_efeitos()
    exemplo_rom_simulation()
    exemplo_busca_carta()
    dicas_engenharia_reversa()
    
    print("\n" + "=" * 60)
    print("PRÓXIMOS PASSOS")
    print("=" * 60)
    print("""
1. Obtenha uma ROM original do Yu-Gi-Oh! Forbidden Memories
2. Execute o programa principal: python3 fm_modifier.py
3. Carregue a ROM e experimente as modificações
4. Teste em um emulador (DuckStation recomendado)
5. Compartilhe suas descobertas com a comunidade!

Boa sorte e divirta-se modificando! 🎮
""")
