#!/usr/bin/env python3
"""
Yu-Gi-Oh! Forbidden Memories ROM Modifier
Ferramenta para modificar o jogo Yu-Gi-Oh! Forbidden Memories (PS1)

Funcionalidades:
- Extrair e modificar dados de cartas
- Editar textos
- Modificar estatísticas das cartas
- Adicionar/modificar efeitos de cartas
- Patch de ROM personalizado
"""

import struct
import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from pathlib import Path


# Constantes de atributos
ATTRIBUTES = {
    0x00: "Nenhum",
    0x01: "Dark",      # Trevas
    0x02: "Earth",     # Terra
    0x03: "Fire",      # Fogo
    0x04: "Light",     # Luz
    0x05: "Water",     # Água
    0x06: "Wind",      # Vento
    0x07: "Divine"     # Divino (raro)
}

# Constantes de tipos
CARD_TYPES = {
    0x00: "Monstro Normal",
    0x01: "Monstro Efeito",
    0x02: "Monstro Ritual",
    0x03: "Monstro Fusão",
    0x04: "Monstro Union",
    0x05: "Monstro Toon",
    0x06: "Monstro Gemini",
    0x07: "Monstro Spirit",
    0x10: "Magia Normal",
    0x11: "Magia Continua",
    0x12: "Magia Equipamento",
    0x13: "Magia Rápida",
    0x14: "Magia Ritual",
    0x15: "Magia Campo",
    0x20: "Armadilha Normal",
    0x21: "Armadilha Continua",
    0x22: "Armadilha Counter"
}

# Efeitos especiais (flags)
EFFECT_FLAGS = {
    0x0001: "Não pode ser destruído em batalha",
    0x0002: "Não pode ser alvo de ataques",
    0x0004: "Ataque direto permitido",
    0x0008: "Pode atacar duas vezes",
    0x0010: "Imune a magias",
    0x0020: "Imune a armadilhas",
    0x0040: "Ganha ATK por turno",
    0x0080: "Drena ATK do oponente",
    0x0100: "Revive automaticamente",
    0x0200: "Banish ao morrer",
    0x0400: "Special Summon gratuito",
    0x0800: "Negate efeitos",
    0x1000: "Muda de posição automático",
    0x2000: "Pesca de carta",
    0x4000: "Dano duplo",
    0x8000: "Invencível"
}


@dataclass
class CardData:
    """Estrutura de dados para uma carta"""
    card_id: int
    name: str
    attack: int
    defense: int
    level: int
    attribute: int  # 1=Dark, 2=Earth, 3=Fire, 4=Light, 5=Water, 6=Wind
    type_: int  # Tipo da carta (monstro, magia, armadilha)
    effect_flags: int = 0  # Flags de efeitos especiais
    description: str = ""
    
    def to_bytes(self) -> bytes:
        """Converte os dados da carta para formato binário"""
        # Formato específico do Forbidden Memories
        data = struct.pack('<H', self.card_id)   # ID da carta (2 bytes)
        data += struct.pack('<H', self.attack)   # ATK (2 bytes)
        data += struct.pack('<H', self.defense)  # DEF (2 bytes)
        data += struct.pack('B', self.level)     # Nível (1 byte)
        data += struct.pack('B', self.attribute) # Atributo (1 byte)
        data += struct.pack('B', self.type_)     # Tipo (1 byte)
        data += struct.pack('<H', self.effect_flags)  # Efeitos (2 bytes)
        return data
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'CardData':
        """Cria objeto CardData a partir de bytes"""
        if len(data) < 11:
            raise ValueError("Dados insuficientes para CardData")
        
        card_id = struct.unpack('<H', data[0:2])[0]
        attack = struct.unpack('<H', data[2:4])[0]
        defense = struct.unpack('<H', data[4:6])[0]
        level = struct.unpack('B', data[6:7])[0]
        attribute = struct.unpack('B', data[7:8])[0]
        type_ = struct.unpack('B', data[8:9])[0]
        effect_flags = struct.unpack('<H', data[9:11])[0] if len(data) >= 11 else 0
        
        return cls(
            card_id=card_id,
            name="",
            attack=attack,
            defense=defense,
            level=level,
            attribute=attribute,
            type_=type_,
            effect_flags=effect_flags,
            description=""
        )
    
    def get_attribute_name(self) -> str:
        """Retorna o nome do atributo"""
        return ATTRIBUTES.get(self.attribute, f"Desconhecido ({self.attribute})")
    
    def get_type_name(self) -> str:
        """Retorna o nome do tipo"""
        return CARD_TYPES.get(self.type_, f"Desconhecido ({self.type_})")
    
    def get_effects_list(self) -> List[str]:
        """Retorna lista de efeitos ativos"""
        effects = []
        for flag, desc in EFFECT_FLAGS.items():
            if self.effect_flags & flag:
                effects.append(desc)
        return effects
    
    def add_effect(self, effect_flag: int):
        """Adiciona um efeito à carta"""
        self.effect_flags |= effect_flag
    
    def remove_effect(self, effect_flag: int):
        """Remove um efeito da carta"""
        self.effect_flags &= ~effect_flag
    
    def has_effect(self, effect_flag: int) -> bool:
        """Verifica se a carta tem um efeito específico"""
        return bool(self.effect_flags & effect_flag)


class ForbiddenMemoriesROM:
    """Classe principal para manipulação da ROM do Forbidden Memories"""
    
    # Offset conhecido onde começam os dados das cartas (pode variar)
    CARD_DATA_OFFSET = 0x80000  # Exemplo - precisa ser ajustado conforme análise
    CARD_SIZE = 11  # Tamanho atualizado com effects_flags
    
    def __init__(self, rom_path: str):
        self.rom_path = Path(rom_path)
        self.data: bytearray = bytearray()
        self.cards: List[CardData] = []
        self.card_index: Dict[int, int] = {}  # Mapeia card_id -> offset
        
    def load_rom(self) -> bool:
        """Carrega a ROM do arquivo"""
        if not self.rom_path.exists():
            print(f"Erro: Arquivo {self.rom_path} não encontrado!")
            return False
        
        with open(self.rom_path, 'rb') as f:
            self.data = bytearray(f.read())
        
        print(f"ROM carregada com sucesso: {len(self.data)} bytes")
        print(f"Tamanho: {len(self.data) / (1024*1024):.2f} MB")
        return True
    
    def save_rom(self, output_path: Optional[str] = None) -> bool:
        """Salva a ROM modificada"""
        if output_path is None:
            output_path = self.rom_path.parent / f"{self.rom_path.stem}_modified{self.rom_path.suffix}"
        else:
            output_path = Path(output_path)
        
        with open(output_path, 'wb') as f:
            f.write(self.data)
        
        print(f"ROM salva em: {output_path}")
        return True
    
    def build_card_index(self, start_offset: int, count: int):
        """Constrói índice de cartas para acesso rápido"""
        self.card_index.clear()
        for i in range(count):
            offset = start_offset + (i * self.CARD_SIZE)
            if offset + self.CARD_SIZE > len(self.data):
                break
            
            card_id = struct.unpack('<H', self.data[offset:offset+2])[0]
            if card_id != 0 and card_id != 0xFFFF:
                self.card_index[card_id] = offset
        
        print(f"Índice construído: {len(self.card_index)} cartas encontradas")
    
    def read_card_data(self, offset: int, count: int) -> List[CardData]:
        """Lê dados de cartas de um offset específico"""
        cards = []
        
        for i in range(count):
            start = offset + (i * self.CARD_SIZE)
            if start + self.CARD_SIZE > len(self.data):
                break
            
            card_data = self.data[start:start + self.CARD_SIZE]
            card = CardData.from_bytes(card_data)
            cards.append(card)
        
        return cards
    
    def get_card_offset(self, card_id: int) -> Optional[int]:
        """Retorna o offset de uma carta pelo ID"""
        if card_id in self.card_index:
            return self.card_index[card_id]
        
        # Busca linear se não estiver no índice
        for i in range(0, len(self.data) - self.CARD_SIZE, 2):
            current_id = struct.unpack('<H', self.data[i:i+2])[0]
            if current_id == card_id:
                return i
        
        return None
    
    def write_card_data(self, offset: int, card: CardData) -> bool:
        """Escreve dados de uma carta em um offset específico"""
        card_bytes = card.to_bytes()
        
        if offset + len(card_bytes) > len(self.data):
            print("Erro: Offset fora dos limites da ROM")
            return False
        
        self.data[offset:offset + len(card_bytes)] = card_bytes
        return True
    
    def modify_card_stats(self, card_id: int, new_attack: int, new_defense: int, 
                         new_level: Optional[int] = None) -> bool:
        """Modifica ATK/DEF e opcionalmente nível de uma carta"""
        offset = self.get_card_offset(card_id)
        
        if offset is None:
            print(f"Carta {card_id} não encontrada")
            return False
        
        # Modifica ATK
        self.data[offset+2:offset+4] = struct.pack('<H', new_attack)
        # Modifica DEF
        self.data[offset+4:offset+6] = struct.pack('<H', new_defense)
        
        # Modifica nível se fornecido
        if new_level is not None:
            self.data[offset+6] = new_level
        
        print(f"Carta {card_id} modificada: ATK={new_attack}, DEF={new_defense}", end="")
        if new_level is not None:
            print(f", Level={new_level}", end="")
        print()
        
        return True
    
    def add_effect_to_card(self, card_id: int, effect_flag: int) -> bool:
        """Adiciona um efeito específico a uma carta"""
        offset = self.get_card_offset(card_id)
        
        if offset is None:
            print(f"Carta {card_id} não encontrada")
            return False
        
        # Lê flags atuais
        current_flags = struct.unpack('<H', self.data[offset+9:offset+11])[0]
        # Adiciona novo efeito
        new_flags = current_flags | effect_flag
        # Escreve de volta
        self.data[offset+9:offset+11] = struct.pack('<H', new_flags)
        
        effect_name = EFFECT_FLAGS.get(effect_flag, f"Efeito 0x{effect_flag:04X}")
        print(f"Efeito '{effect_name}' adicionado à carta {card_id}")
        
        return True
    
    def remove_effect_from_card(self, card_id: int, effect_flag: int) -> bool:
        """Remove um efeito específico de uma carta"""
        offset = self.get_card_offset(card_id)
        
        if offset is None:
            print(f"Carta {card_id} não encontrada")
            return False
        
        # Lê flags atuais
        current_flags = struct.unpack('<H', self.data[offset+9:offset+11])[0]
        # Remove efeito
        new_flags = current_flags & ~effect_flag
        # Escreve de volta
        self.data[offset+9:offset+11] = struct.pack('<H', new_flags)
        
        effect_name = EFFECT_FLAGS.get(effect_flag, f"Efeito 0x{effect_flag:04X}")
        print(f"Efeito '{effect_name}' removido da carta {card_id}")
        
        return True
    
    def set_all_effects(self, card_id: int, effect_flags: int) -> bool:
        """Define todas as flags de efeito de uma carta"""
        offset = self.get_card_offset(card_id)
        
        if offset is None:
            print(f"Carta {card_id} não encontrada")
            return False
        
        self.data[offset+9:offset+11] = struct.pack('<H', effect_flags)
        print(f"Efeitos da carta {card_id} definidos para: 0x{effect_flags:04X}")
        
        return True
    
    def get_card_info(self, card_id: int) -> Optional[CardData]:
        """Retorna informações completas de uma carta"""
        offset = self.get_card_offset(card_id)
        
        if offset is None:
            return None
        
        card_data = self.data[offset:offset + self.CARD_SIZE]
        return CardData.from_bytes(card_data)
    
    def list_available_effects(self):
        """Lista todos os efeitos disponíveis"""
        print("\n=== Efeitos Disponíveis ===")
        for flag, desc in EFFECT_FLAGS.items():
            print(f"  0x{flag:04X} - {desc}")
        print()
    
    def create_patch(self, original_rom: str, modified_rom: str, patch_path: str) -> bool:
        """Cria um patch IPS/APS entre duas ROMs"""
        # Implementação simplificada de patch IPS
        with open(original_rom, 'rb') as f:
            original_data = bytearray(f.read())
        
        with open(modified_rom, 'rb') as f:
            modified_data = bytearray(f.read())
        
        patch_data = bytearray()
        patch_data.extend(b'PATCH')  # Header IPS
        
        i = 0
        while i < min(len(original_data), len(modified_data)):
            if original_data[i] != modified_data[i]:
                # Início de bloco modificado
                start = i
                while i < len(original_data) and i < len(modified_data) and original_data[i] != modified_data[i]:
                    i += 1
                
                # Escreve offset (3 bytes, big-endian)
                patch_data.extend(struct.pack('>I', start)[1:])
                # Escreve tamanho (2 bytes, big-endian)
                patch_data.extend(struct.pack('>H', i - start))
                # Escreve dados
                patch_data.extend(modified_data[start:i])
            else:
                i += 1
        
        # EOF marker
        patch_data.extend(b'EOF')
        
        with open(patch_path, 'wb') as f:
            f.write(patch_data)
        
        print(f"Patch criado: {patch_path}")
        return True


def main():
    """Função principal com menu interativo"""
    print("=" * 60)
    print("Yu-Gi-Oh! Forbidden Memories ROM Modifier")
    print("Modifique cartas e adicione efeitos especiais!")
    print("=" * 60)
    print()
    
    rom_modifier = None
    
    while True:
        print("\n=== Menu Principal ===")
        print("1. Carregar ROM")
        print("2. Modificar estatísticas de carta (ATK/DEF/Level)")
        print("3. Adicionar efeito a uma carta")
        print("4. Remover efeito de uma carta")
        print("5. Definir todos os efeitos de uma carta")
        print("6. Ver informações de uma carta")
        print("7. Listar efeitos disponíveis")
        print("8. Salvar ROM modificada")
        print("9. Criar patch IPS")
        print("0. Sair")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == '1':
            rom_path = input("Caminho da ROM (.bin, .img): ").strip()
            rom_modifier = ForbiddenMemoriesROM(rom_path)
            if rom_modifier.load_rom():
                # Tenta construir índice automaticamente
                offset_input = input("Offset inicial das cartas (hex, ex: 80000) ou Enter para padrão: ").strip()
                if offset_input:
                    start_offset = int(offset_input, 16)
                else:
                    start_offset = rom_modifier.CARD_DATA_OFFSET
                
                count_input = input("Número estimado de cartas ou Enter para 1000: ").strip()
                count = int(count_input) if count_input else 1000
                
                rom_modifier.build_card_index(start_offset, count)
        
        elif choice == '2':
            if rom_modifier is None:
                print("Carregue uma ROM primeiro!")
                continue
            
            card_id = int(input("ID da carta: "))
            new_atk = int(input("Novo ATK: "))
            new_def = int(input("Novo DEF: "))
            level_input = input("Novo Level (ou Enter para manter): ").strip()
            new_level = int(level_input) if level_input else None
            
            rom_modifier.modify_card_stats(card_id, new_atk, new_def, new_level)
        
        elif choice == '3':
            if rom_modifier is None:
                print("Carregue uma ROM primeiro!")
                continue
            
            rom_modifier.list_available_effects()
            card_id = int(input("ID da carta: "))
            effect_hex = input("Código do efeito em hex (ex: 0001): ").strip()
            effect_flag = int(effect_hex, 16)
            
            rom_modifier.add_effect_to_card(card_id, effect_flag)
        
        elif choice == '4':
            if rom_modifier is None:
                print("Carregue uma ROM primeiro!")
                continue
            
            rom_modifier.list_available_effects()
            card_id = int(input("ID da carta: "))
            effect_hex = input("Código do efeito em hex (ex: 0001): ").strip()
            effect_flag = int(effect_hex, 16)
            
            rom_modifier.remove_effect_from_card(card_id, effect_flag)
        
        elif choice == '5':
            if rom_modifier is None:
                print("Carregue uma ROM primeiro!")
                continue
            
            card_id = int(input("ID da carta: "))
            effects_hex = input("Flags de efeito em hex (ex: 00FF): ").strip()
            effect_flags = int(effects_hex, 16)
            
            rom_modifier.set_all_effects(card_id, effect_flags)
        
        elif choice == '6':
            if rom_modifier is None:
                print("Carregue uma ROM primeiro!")
                continue
            
            card_id = int(input("ID da carta: "))
            card_info = rom_modifier.get_card_info(card_id)
            
            if card_info:
                print(f"\n=== Informações da Carta {card_id} ===")
                print(f"ATK: {card_info.attack}")
                print(f"DEF: {card_info.defense}")
                print(f"Level: {card_info.level}")
                print(f"Atributo: {card_info.get_attribute_name()}")
                print(f"Tipo: {card_info.get_type_name()}")
                print(f"Efeitos: {card_info.get_effects_list() if card_info.get_effects_list() else 'Nenhum'}")
            else:
                print(f"Carta {card_id} não encontrada!")
        
        elif choice == '7':
            if rom_modifier:
                rom_modifier.list_available_effects()
            else:
                # Mostra efeitos mesmo sem ROM carregada
                print("\n=== Efeitos Disponíveis ===")
                for flag, desc in EFFECT_FLAGS.items():
                    print(f"  0x{flag:04X} - {desc}")
                print()
        
        elif choice == '8':
            if rom_modifier is None:
                print("Carregue uma ROM primeiro!")
                continue
            
            output = input("Nome do arquivo de saída (Enter para padrão): ").strip()
            rom_modifier.save_rom(output if output else None)
        
        elif choice == '9':
            original = input("ROM original: ").strip()
            modified = input("ROM modificada: ").strip()
            patch_file = input("Nome do patch: ").strip()
            
            if all([original, modified, patch_file]):
                temp_rom = ForbiddenMemoriesROM(original)
                temp_rom.create_patch(original, modified, patch_file)
        
        elif choice == '0':
            print("Saindo...")
            break
        
        else:
            print("Opção inválida!")


if __name__ == "__main__":
    main()
