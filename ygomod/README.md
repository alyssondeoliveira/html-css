# Yu-Gi-Oh! Forbidden Memories ROM Modifier

Ferramenta em Python para modificar o jogo **Yu-Gi-Oh! Forbidden Memories** do PlayStation 1.

## ⚠️ Aviso Legal

Este projeto é apenas para fins educacionais. Você deve possuir uma cópia original do jogo para usar esta ferramenta. Não distribua ROMs protegidas por direitos autorais.

## Funcionalidades

- 🃏 Modificar estatísticas das cartas (ATK/DEF/Level)
- ✨ **Adicionar e remover efeitos especiais nas cartas**
- 🔍 Visualizar informações completas das cartas
- 📝 Extrair e editar dados das cartas
- 🔧 Criar patches IPS para compartilhamento
- 💾 Salvar ROMs modificadas
- 📊 Índice de busca rápida de cartas

## Efeitos Especiais Disponíveis

A ferramenta suporta os seguintes efeitos que podem ser aplicados às cartas:

| Código | Efeito |
|--------|--------|
| 0x0001 | Não pode ser destruído em batalha |
| 0x0002 | Não pode ser alvo de ataques |
| 0x0004 | Ataque direto permitido |
| 0x0008 | Pode atacar duas vezes |
| 0x0010 | Imune a magias |
| 0x0020 | Imune a armadilhas |
| 0x0040 | Ganha ATK por turno |
| 0x0080 | Drena ATK do oponente |
| 0x0100 | Revive automaticamente |
| 0x0200 | Banish ao morrer |
| 0x0400 | Special Summon gratuito |
| 0x0800 | Negate efeitos |
| 0x1000 | Muda de posição automático |
| 0x2000 | Pesca de carta |
| 0x4000 | Dano duplo |
| 0x8000 | Invencível |

## Requisitos

- Python 3.7+
- Uma ROM do Yu-Gi-Oh! Forbidden Memories (formato .bin, .img, .pbp, etc.)

## Instalação

```bash
# Clone ou copie este diretório
cd ygomod

# O script não requer dependências externas (usa apenas biblioteca padrão)
python3 fm_modifier.py
```

## Uso

### Modo Interativo

Execute o script e siga o menu:

```bash
python3 fm_modifier.py
```

Opções disponíveis:
1. **Carregar ROM** - Carrega o arquivo da ROM e constrói índice de cartas
2. **Modificar estatísticas** - Altera ATK/DEF/Level de uma carta específica
3. **Adicionar efeito** - Adiciona um efeito especial a uma carta
4. **Remover efeito** - Remove um efeito especial de uma carta
5. **Definir todos os efeitos** - Define manualmente todas as flags de efeito
6. **Ver informações** - Mostra dados completos de uma carta (ATK, DEF, Level, Atributo, Tipo, Efeitos)
7. **Listar efeitos** - Exibe todos os efeitos disponíveis com seus códigos
8. **Salvar ROM modificada** - Salva as alterações em um novo arquivo
9. **Criar patch IPS** - Gera um patch IPS das modificações
0. **Sair**

### Exemplo de Sessão

```
=== Menu Principal ===
1. Carregar ROM
2. Modificar estatísticas de carta (ATK/DEF/Level)
3. Adicionar efeito a uma carta
...

Escolha uma opção: 1
Caminho da ROM (.bin, .img): /path/to/rom.bin
ROM carregada com sucesso: 681574400 bytes
Tamanho: 650.00 MB
Offset inicial das cartas (hex, ex: 80000) ou Enter para padrão: 
Número estimado de cartas ou Enter para 1000: 
Índice construído: 750 cartas encontradas

Escolha uma opção: 3

=== Efeitos Disponíveis ===
  0x0001 - Não pode ser destruído em batalha
  0x0002 - Não pode ser alvo de ataques
  ...

ID da carta: 123
Código do efeito em hex (ex: 0001): 0001
Efeito 'Não pode ser destruído em batalha' adicionado à carta 123
```

### Uso Programático

```python
from fm_modifier import ForbiddenMemoriesROM, CardData, EFFECT_FLAGS

# Carregar ROM
rom = ForbiddenMemoriesROM("caminho/para/rom.bin")
rom.load_rom()

# Construir índice de cartas (precisa do offset correto)
rom.build_card_index(start_offset=0x80000, count=1000)

# Modificar estatísticas de uma carta
rom.modify_card_stats(card_id=1, new_attack=3000, new_defense=2500, new_level=8)

# Adicionar efeito "Imune a magias" (0x0010)
rom.add_effect_to_card(card_id=1, effect_flag=0x0010)

# Adicionar múltiplos efeitos
rom.add_effect_to_card(card_id=1, effect_flag=0x0001)  # Não destruído em batalha
rom.add_effect_to_card(card_id=1, effect_flag=0x0008)  # Ataca duas vezes

# Ver informações da carta
card = rom.get_card_info(card_id=1)
if card:
    print(f"Carta {card.card_id}:")
    print(f"  ATK: {card.attack}, DEF: {card.defense}, Level: {card.level}")
    print(f"  Atributo: {card.get_attribute_name()}")
    print(f"  Tipo: {card.get_type_name()}")
    print(f"  Efeitos: {card.get_effects_list()}")

# Definir todos os efeitos de uma vez
rom.set_all_effects(card_id=1, effect_flags=0x001B)  # Combinação de efeitos

# Remover um efeito específico
rom.remove_effect_from_card(card_id=1, effect_flag=0x0010)

# Salvar ROM modificada
rom.save_rom("rom_modificada.bin")

# Ou criar um patch
rom.create_patch("original.bin", "modificada.bin", "patch.ips")
```

## Estrutura dos Dados

O formato interno das cartas no Forbidden Memories segue esta estrutura:

| Campo       | Tamanho | Descrição                    |
|-------------|---------|------------------------------|
| ID          | 2 bytes | Identificador único da carta |
| ATK         | 2 bytes | Pontos de ataque             |
| DEF         | 2 bytes | Pontos de defesa             |
| Level       | 1 byte  | Nível da carta               |
| Attribute   | 1 byte  | Atributo (Dark, Light, etc.) |
| Type        | 1 byte  | Tipo (Monstro, Magia, etc.)  |
| Effect Flags| 2 bytes | Flags de efeitos especiais   |

**Total:** 11 bytes por carta

### Atributos

| Valor | Nome   |
|-------|--------|
| 0x00  | Nenhum |
| 0x01  | Dark   |
| 0x02  | Earth  |
| 0x03  | Fire   |
| 0x04  | Light  |
| 0x05  | Water  |
| 0x06  | Wind   |
| 0x07  | Divine |

### Tipos de Carta

| Valor | Tipo            |
|-------|-----------------|
| 0x00  | Monstro Normal  |
| 0x01  | Monstro Efeito  |
| 0x02  | Monstro Ritual  |
| 0x03  | Monstro Fusão   |
| 0x10  | Magia Normal    |
| 0x11  | Magia Continua  |
| 0x12  | Magia Equipamento |
| 0x20  | Armadilha Normal |
| 0x21  | Armadilha Continua |

**Nota:** Os offsets exatos podem variar. É necessário fazer engenharia reversa da ROM para localizar as tabelas de dados corretas. Diferentes versões do jogo (NTSC-U, NTSC-J, PAL) podem ter offsets diferentes.

## Próximos Passos / Melhorias Futuras

- [ ] Mapeamento completo dos offsets da ROM para cada versão
- [ ] Editor de nomes de cartas (codificação específica)
- [ ] Suporte a textos em português
- [ ] Interface gráfica (Tkinter ou PyQt)
- [ ] Banco de dados de IDs das cartas com nomes
- [ ] Exportação/importação de cartas em JSON
- [ ] Suporte a múltiplas versões do jogo (NTSC-U, NTSC-J, PAL)
- [ ] Busca de cartas por nome
- [ ] Histórico de modificações
- [ ] Backup automático antes de modificar

## Recursos Úteis

- [Romhacking.net](https://www.romhacking.net/) - Ferramentas e tutoriais
- [PSX Data Center](http://psxdatacenter.com/) - Documentação técnica do PS1
- [GameFAQs - Forbidden Memories](https://gamefaqs.gamespot.com/ps/197343-yu-gi-oh-forbidden-memories) - Informações do jogo
- [Zenology's FM Guide](https://gamefaqs.gamespot.com/ps/197343-yu-gi-oh-forbidden-memories/faqs/26182) - Lista completa de cartas

## Contribuição

Sinta-se à vontade para melhorar este projeto! Algumas áreas que precisam de trabalho:

1. **Engenharia reversa** - Descobrir os offsets exatos dos dados para cada versão
2. **Codificação de texto** - Entender como os nomes das cartas são armazenados
3. **Testes** - Validar as modificações em emuladores (ePSXE, DuckStation) ou console real
4. **Documentação** - Adicionar mais exemplos e tutoriais

## Dicas de Engenharia Reversa

Para encontrar os offsets corretos dos dados das cartas:

1. Use um emulador com debugger (ePSXE, DuckStation)
2. Procure por valores conhecidos (ATK/DEF de cartas famosas)
3. Use ferramentas de busca hexadecimal na ROM
4. Consulte documentação existente de ROM hacking de FM

## Licença

MIT License - Use por sua conta e risco.

---

**Desenvolvido com ❤️ para a comunidade de Yu-Gi-Oh!**
