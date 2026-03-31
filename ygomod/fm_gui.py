#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yu-Gi-Oh! Forbidden Memories - Modificador de Cartas com Interface Gráfica
Ferramenta para modificar cartas do jogo de PlayStation 1
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import struct
import os
import json

class Carta:
    """Classe que representa uma carta do jogo"""
    
    # Efeitos disponíveis
    EFEITOS = {
        0x00: "Nenhum",
        0x01: "Fusão",
        0x02: "Invocação Especial",
        0x03: "Descartar para ativar",
        0x04: "Destrói monstro em batalha",
        0x05: "Volta para mão",
        0x06: "Troca de controle",
        0x07: "Reduz ATK/DEF",
        0x08: "Aumenta ATK/DEF",
        0x09: "Muda posição de batalha",
        0x0A: "Negar magia/armadilha",
        0x0B: "Destrói todas as cartas",
        0x0C: "Revive monstro",
        0x0D: "Compra cartas",
        0x0E: "Dano direto",
        0x0F: "Proteção contra efeitos"
    }
    
    ATRIBUTOS = {
        0x01: "TREVAS",
        0x02: "LUZ",
        0x03: "TERRA",
        0x04: "FOGO",
        0x05: "ÁGUA",
        0x06: "VENTO",
        0x07: "THUMBER"
    }
    
    TIPOS = {
        0x01: "Guerreiro",
        0x02: "Mago",
        0x03: "Dragão",
        0x04: "Zumbi",
        0x05: "Besta",
        0x06: "Besta Guerreira",
        0x07: "Demônio",
        0x08: "Fada",
        0x09: "Inseto",
        0x0A: "Dinossauro",
        0x0B: "Réptil",
        0x0C: "Peixe",
        0x0D: "Máquina",
        0x0E: "Pyro",
        0x0F: "Rocha",
        0x10: "Ave",
        0x11: "Planta",
        0x12: "Elétrico"
    }

    def __init__(self, id_carta=0, nome="Carta Desconhecida", ataque=0, defesa=0, 
                 nivel=0, atributo=0, tipo=0, efeito=0, descricao=""):
        self.id_carta = id_carta
        self.nome = nome
        self.ataque = ataque
        self.defesa = defesa
        self.nivel = nivel
        self.atributo = atributo
        self.tipo = tipo
        self.efeito = efeito
        self.descricao = descricao
    
    def get_nome_atributo(self):
        return self.ATRIBUTOS.get(self.atributo, "Desconhecido")
    
    def get_nome_tipo(self):
        return self.TIPOS.get(self.tipo, "Desconhecido")
    
    def get_nome_efeito(self):
        return self.EFEITOS.get(self.efeito, "Desconhecido")


class FMRomModifier:
    """Classe principal para modificar a ROM"""
    
    def __init__(self):
        self.rom_data = None
        self.rom_path = None
        self.cartas_modificadas = {}
        
    def carregar_rom(self, caminho):
        """Carrega a ROM do jogo"""
        try:
            with open(caminho, 'rb') as f:
                self.rom_data = bytearray(f.read())
            self.rom_path = caminho
            return True, f"ROM carregada com sucesso!\nTamanho: {len(self.rom_data)} bytes"
        except Exception as e:
            return False, f"Erro ao carregar ROM: {str(e)}"
    
    def salvar_rom(self, caminho=None):
        """Salva a ROM modificada"""
        if self.rom_data is None:
            return False, "Nenhuma ROM carregada"
        
        if caminho is None:
            caminho = self.rom_path.replace('.bin', '_modificado.bin').replace('.img', '_modificado.img')
        
        try:
            with open(caminho, 'wb') as f:
                f.write(self.rom_data)
            return True, f"ROM salva com sucesso em: {caminho}"
        except Exception as e:
            return False, f"Erro ao salvar ROM: {str(e)}"
    
    def modificar_carta(self, id_carta, novos_valores):
        """
        Modifica os dados de uma carta
        novos_valores: dict com chaves como 'ataque', 'defesa', 'efeito', etc.
        """
        if self.rom_data is None:
            return False, "Nenhuma ROM carregada"
        
        # NOTA: Os offsets reais precisam ser descobertos via engenharia reversa
        # Este é um exemplo de estrutura
        offset_base = 0x100000 + (id_carta * 32)  # Offset fictício
        
        if offset_base + 32 > len(self.rom_data):
            return False, "Offset fora dos limites da ROM"
        
        # Armazena as modificações
        self.cartas_modificadas[id_carta] = novos_valores
        
        return True, f"Carta {id_carta} marcada para modificação"
    
    def gerar_patch_ips(self, caminho_saida):
        """Gera um patch IPS com as modificações"""
        if not self.cartas_modificadas:
            return False, "Nenhuma modificação para aplicar"
        
        # Implementação simplificada do formato IPS
        patch_data = bytearray()
        patch_data.extend(b'PATCH')  # Header IPS
        
        # Adiciona as modificações (exemplo)
        for id_carta, valores in self.cartas_modificadas.items():
            offset = 0x100000 + (id_carta * 32)
            # Dados fictícios para exemplo
            dados = struct.pack('<HHBBBB', 
                              valores.get('ataque', 0),
                              valores.get('defesa', 0),
                              valores.get('nivel', 0),
                              valores.get('atributo', 0),
                              valores.get('tipo', 0),
                              valores.get('efeito', 0))
            
            # Formato IPS: offset (3 bytes) + tamanho (2 bytes) + dados
            patch_data.append((offset >> 16) & 0xFF)
            patch_data.append((offset >> 8) & 0xFF)
            patch_data.append(offset & 0xFF)
            patch_data.append(0x00)
            patch_data.append(len(dados))
            patch_data.extend(dados)
        
        patch_data.extend(b'EOF')  # Footer IPS
        
        try:
            with open(caminho_saida, 'wb') as f:
                f.write(patch_data)
            return True, f"Patch IPS gerado: {caminho_saida}"
        except Exception as e:
            return False, f"Erro ao gerar patch: {str(e)}"


class InterfaceGrafica:
    """Interface gráfica principal"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Yu-Gi-Oh! FM - Modificador de Cartas")
        self.root.geometry("900x700")
        
        self.modifier = FMRomModifier()
        self.cartas_carregadas = []
        self.carta_selecionada = None
        
        self.setup_ui()
        self.carregar_cartas_exemplo()
    
    def setup_ui(self):
        """Configura a interface gráfica"""
        # Frame superior - Controles de ROM
        frame_rom = ttk.LabelFrame(self.root, text="ROM do Jogo", padding=10)
        frame_rom.pack(fill='x', padx=10, pady=5)
        
        btn_carregar = ttk.Button(frame_rom, text="Carregar ROM", command=self.carregar_rom)
        btn_carregar.pack(side='left', padx=5)
        
        btn_salvar = ttk.Button(frame_rom, text="Salvar ROM", command=self.salvar_rom)
        btn_salvar.pack(side='left', padx=5)
        
        btn_patch = ttk.Button(frame_rom, text="Gerar Patch IPS", command=self.gerar_patch)
        btn_patch.pack(side='left', padx=5)
        
        self.lbl_status_rom = ttk.Label(frame_rom, text="Nenhuma ROM carregada", foreground='gray')
        self.lbl_status_rom.pack(side='right', padx=10)
        
        # Frame principal dividido em duas partes
        frame_principal = ttk.PanedWindow(self.root, orient='horizontal')
        frame_principal.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Lado esquerdo - Lista de cartas
        frame_lista = ttk.LabelFrame(frame_principal, text="Lista de Cartas", padding=10)
        frame_principal.add(frame_lista, weight=1)
        
        # Treeview para lista de cartas
        colunas = ('ID', 'Nome', 'ATK', 'DEF', 'Tipo', 'Atributo')
        self.tree_cartas = ttk.Treeview(frame_lista, columns=colunas, show='headings', height=20)
        
        for col in colunas:
            self.tree_cartas.heading(col, text=col)
            self.tree_cartas.column(col, width=80)
        
        self.tree_cartas.column('Nome', width=200)
        
        scrollbar = ttk.Scrollbar(frame_lista, orient='vertical', command=self.tree_cartas.yview)
        self.tree_cartas.configure(yscrollcommand=scrollbar.set)
        
        self.tree_cartas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.tree_cartas.bind('<<TreeviewSelect>>', self.selecionar_carta)
        
        # Lado direito - Editor de carta
        frame_editor = ttk.LabelFrame(frame_principal, text="Editor de Carta", padding=10)
        frame_principal.add(frame_editor, weight=2)
        
        # Informações da carta
        frame_info = ttk.Frame(frame_editor)
        frame_info.pack(fill='x', pady=5)
        
        ttk.Label(frame_info, text="ID da Carta:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.entry_id = ttk.Entry(frame_info, width=10, state='readonly')
        self.entry_id.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(frame_info, text="Nome:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.entry_nome = ttk.Entry(frame_info, width=30)
        self.entry_nome.grid(row=0, column=3, sticky='w', padx=5, pady=2)
        
        # Estatísticas
        frame_stats = ttk.LabelFrame(frame_editor, text="Estatísticas", padding=10)
        frame_stats.pack(fill='x', pady=5)
        
        ttk.Label(frame_stats, text="ATK:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.spin_atk = ttk.Spinbox(frame_stats, from_=0, to=9999, width=10)
        self.spin_atk.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(frame_stats, text="DEF:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.spin_def = ttk.Spinbox(frame_stats, from_=0, to=9999, width=10)
        self.spin_def.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(frame_stats, text="Nível:").grid(row=0, column=4, sticky='w', padx=5, pady=2)
        self.spin_nivel = ttk.Spinbox(frame_stats, from_=1, to=12, width=5)
        self.spin_nivel.grid(row=0, column=5, padx=5, pady=2)
        
        # Tipo e Atributo
        frame_props = ttk.LabelFrame(frame_editor, text="Propriedades", padding=10)
        frame_props.pack(fill='x', pady=5)
        
        ttk.Label(frame_props, text="Tipo:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.combo_tipo = ttk.Combobox(frame_props, values=list(Carta.TIPOS.values()), width=20, state='readonly')
        self.combo_tipo.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(frame_props, text="Atributo:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.combo_atributo = ttk.Combobox(frame_props, values=list(Carta.ATRIBUTOS.values()), width=15, state='readonly')
        self.combo_atributo.grid(row=0, column=3, padx=5, pady=2)
        
        # Efeito especial
        frame_efeito = ttk.LabelFrame(frame_editor, text="Efeito Especial", padding=10)
        frame_efeito.pack(fill='x', pady=5)
        
        ttk.Label(frame_efeito, text="Efeito:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.combo_efeito = ttk.Combobox(frame_efeito, values=list(Carta.EFEITOS.values()), width=40, state='readonly')
        self.combo_efeito.grid(row=0, column=1, padx=5, pady=2)
        
        # Descrição
        ttk.Label(frame_efeito, text="Descrição:").grid(row=1, column=0, sticky='nw', padx=5, pady=2)
        self.text_descricao = scrolledtext.ScrolledText(frame_efeito, width=50, height=4)
        self.text_descricao.grid(row=1, column=1, padx=5, pady=2)
        
        # Botões de ação
        frame_botoes = ttk.Frame(frame_editor)
        frame_botoes.pack(fill='x', pady=10)
        
        btn_aplicar = ttk.Button(frame_botoes, text="Aplicar Modificações", command=self.aplicar_modificacoes)
        btn_aplicar.pack(side='left', padx=5)
        
        btn_reset = ttk.Button(frame_botoes, text="Resetar", command=self.resetar_formulario)
        btn_reset.pack(side='left', padx=5)
        
        btn_buscar = ttk.Button(frame_botoes, text="Buscar Carta por ID", command=self.buscar_carta)
        btn_buscar.pack(side='right', padx=5)
        
        self.entry_busca_id = ttk.Entry(frame_botoes, width=10)
        self.entry_busca_id.pack(side='right', padx=5)
        
        # Frame inferior - Log
        frame_log = ttk.LabelFrame(self.root, text="Log de Operações", padding=10)
        frame_log.pack(fill='both', expand=False, padx=10, pady=5)
        
        self.text_log = scrolledtext.ScrolledText(frame_log, height=6, state='disabled')
        self.text_log.pack(fill='both', expand=True)
    
    def log(self, mensagem):
        """Adiciona mensagem ao log"""
        self.text_log.config(state='normal')
        self.text_log.insert('end', f"{mensagem}\n")
        self.text_log.see('end')
        self.text_log.config(state='disabled')
    
    def carregar_cartas_exemplo(self):
        """Carrega cartas de exemplo para demonstração"""
        cartas_exemplo = [
            Carta(1, "Dragão Branco de Olhos Azuis", 3000, 2500, 8, 0x02, 0x03, 0x00, "Um dragão lendário com poder destrutivo imenso."),
            Carta(2, "Mago Negro", 2500, 2100, 7, 0x01, 0x02, 0x00, "O mago mais poderoso em trevas e luz."),
            Carta(3, "Kuriboh", 300, 200, 1, 0x01, 0x05, 0x05, "Quando descartado, reduz dano de batalha."),
            Carta(4, "Dragão Vermelho de Olhos Negros", 2400, 2000, 7, 0x01, 0x03, 0x04, "Ataca com fúria implacável."),
            Carta(5, "Gaia o Cavaleiro Feroz", 2300, 2100, 7, 0x03, 0x01, 0x00, "Um cavaleiro que monta em um dragão."),
            Carta(6, "Ceifador de Almas", 2200, 1500, 6, 0x01, 0x07, 0x04, "Destrói monstros em batalha facilmente."),
            Carta(7, "Jinzo", 2400, 1500, 6, 0x01, 0x0D, 0x0A, "Anula todas as cartas de armadilha."),
            Carta(8, "Valkyrie dos Segundos", 1700, 1300, 4, 0x02, 0x08, 0x08, "Aumenta ATK durante a batalha."),
        ]
        
        self.cartas_carregadas = cartas_exemplo
        
        for carta in cartas_exemplo:
            self.tree_cartas.insert('', 'end', values=(
                carta.id_carta,
                carta.nome[:25],
                carta.ataque,
                carta.defesa,
                carta.get_nome_tipo(),
                carta.get_nome_atributo()
            ))
        
        self.log("Cartas de exemplo carregadas")
    
    def carregar_rom(self):
        """Abre diálogo para carregar ROM"""
        caminho = filedialog.askopenfilename(
            title="Selecionar ROM do Yu-Gi-Oh! Forbidden Memories",
            filetypes=[("ROM PS1", "*.bin *.img *.iso"), ("Todos os arquivos", "*.*")]
        )
        
        if caminho:
            sucesso, msg = self.modifier.carregar_rom(caminho)
            if sucesso:
                self.lbl_status_rom.config(text=f"ROM: {os.path.basename(caminho)}", foreground='green')
                self.log(msg)
            else:
                messagebox.showerror("Erro", msg)
                self.log(f"ERRO: {msg}")
    
    def salvar_rom(self):
        """Salva a ROM modificada"""
        if self.modifier.rom_data is None:
            messagebox.showwarning("Aviso", "Nenhuma ROM carregada!")
            return
        
        caminho = filedialog.asksaveasfilename(
            title="Salvar ROM Modificada",
            defaultextension=".bin",
            filetypes=[("ROM PS1", "*.bin"), ("Todos os arquivos", "*.*")]
        )
        
        if caminho:
            sucesso, msg = self.modifier.salvar_rom(caminho)
            if sucesso:
                self.log(msg)
                messagebox.showinfo("Sucesso", msg)
            else:
                messagebox.showerror("Erro", msg)
    
    def gerar_patch(self):
        """Gera patch IPS"""
        if not self.modifier.cartas_modificadas:
            messagebox.showwarning("Aviso", "Nenhuma modificação aplicada!")
            return
        
        caminho = filedialog.asksaveasfilename(
            title="Salvar Patch IPS",
            defaultextension=".ips",
            filetypes=[("Patch IPS", "*.ips"), ("Todos os arquivos", "*.*")]
        )
        
        if caminho:
            sucesso, msg = self.modifier.gerar_patch_ips(caminho)
            if sucesso:
                self.log(msg)
                messagebox.showinfo("Sucesso", msg)
            else:
                messagebox.showerror("Erro", msg)
    
    def selecionar_carta(self, event):
        """Preenche o formulário com dados da carta selecionada"""
        selecao = self.tree_cartas.selection()
        if not selecao:
            return
        
        item = self.tree_cartas.item(selecao[0])
        valores = item['values']
        id_carta = int(valores[0])
        
        # Busca a carta na lista
        for carta in self.cartas_carregadas:
            if carta.id_carta == id_carta:
                self.carta_selecionada = carta
                self.preencher_formulario(carta)
                break
    
    def preencher_formulario(self, carta):
        """Preenche os campos do formulário com dados da carta"""
        self.entry_id.config(state='normal')
        self.entry_id.delete(0, 'end')
        self.entry_id.insert(0, str(carta.id_carta))
        self.entry_id.config(state='readonly')
        
        self.entry_nome.delete(0, 'end')
        self.entry_nome.insert(0, carta.nome)
        
        self.spin_atk.delete(0, 'end')
        self.spin_atk.insert(0, str(carta.ataque))
        
        self.spin_def.delete(0, 'end')
        self.spin_def.insert(0, str(carta.defesa))
        
        self.spin_nivel.delete(0, 'end')
        self.spin_nivel.insert(0, str(carta.nivel))
        
        # Seleciona tipo
        nome_tipo = carta.get_nome_tipo()
        if nome_tipo in self.combo_tipo['values']:
            self.combo_tipo.set(nome_tipo)
        
        # Seleciona atributo
        nome_atributo = carta.get_nome_atributo()
        if nome_atributo in self.combo_atributo['values']:
            self.combo_atributo.set(nome_atributo)
        
        # Seleciona efeito
        nome_efeito = carta.get_nome_efeito()
        if nome_efeito in self.combo_efeito['values']:
            self.combo_efeito.set(nome_efeito)
        
        self.text_descricao.delete('1.0', 'end')
        self.text_descricao.insert('1.0', carta.descricao)
    
    def aplicar_modificacoes(self):
        """Aplica as modificações da carta atual"""
        if self.carta_selecionada is None:
            messagebox.showwarning("Aviso", "Selecione uma carta primeiro!")
            return
        
        try:
            # Coleta os valores do formulário
            novos_valores = {
                'nome': self.entry_nome.get(),
                'ataque': int(self.spin_atk.get()),
                'defesa': int(self.spin_def.get()),
                'nivel': int(self.spin_nivel.get()),
                'descricao': self.text_descricao.get('1.0', 'end').strip()
            }
            
            # Converte tipo e atributo de volta para códigos
            tipo_selecionado = self.combo_tipo.get()
            for codigo, nome in Carta.TIPOS.items():
                if nome == tipo_selecionado:
                    novos_valores['tipo'] = codigo
                    break
            
            atributo_selecionado = self.combo_atributo.get()
            for codigo, nome in Carta.ATRIBUTOS.items():
                if nome == atributo_selecionado:
                    novos_valores['atributo'] = codigo
                    break
            
            efeito_selecionado = self.combo_efeito.get()
            for codigo, nome in Carta.EFEITOS.items():
                if nome == efeito_selecionado:
                    novos_valores['efeito'] = codigo
                    break
            
            # Atualiza a carta
            self.carta_selecionada.nome = novos_valores['nome']
            self.carta_selecionada.ataque = novos_valores['ataque']
            self.carta_selecionada.defesa = novos_valores['defesa']
            self.carta_selecionada.nivel = novos_valores['nivel']
            self.carta_selecionada.tipo = novos_valores.get('tipo', self.carta_selecionada.tipo)
            self.carta_selecionada.atributo = novos_valores.get('atributo', self.carta_selecionada.atributo)
            self.carta_selecionada.efeito = novos_valores.get('efeito', self.carta_selecionada.efeito)
            self.carta_selecionada.descricao = novos_valores['descricao']
            
            # Marca para modificação na ROM
            self.modifier.modificar_carta(self.carta_selecionada.id_carta, novos_valores)
            
            # Atualiza a treeview
            selecao = self.tree_cartas.selection()
            if selecao:
                item = self.tree_cartas.item(selecao[0])
                self.tree_cartas.item(selecao[0], values=(
                    self.carta_selecionada.id_carta,
                    self.carta_selecionada.nome[:25],
                    self.carta_selecionada.ataque,
                    self.carta_selecionada.defesa,
                    self.carta_selecionada.get_nome_tipo(),
                    self.carta_selecionada.get_nome_atributo()
                ))
            
            self.log(f"Carta '{self.carta_selecionada.nome}' modificada com sucesso!")
            messagebox.showinfo("Sucesso", f"Modificações aplicadas em: {self.carta_selecionada.nome}")
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Valores inválidos: {str(e)}")
    
    def resetar_formulario(self):
        """Reseta o formulário"""
        if self.carta_selecionada:
            self.preencher_formulario(self.carta_selecionada)
            self.log("Formulário resetado")
    
    def buscar_carta(self):
        """Busca carta por ID"""
        try:
            id_busca = int(self.entry_busca_id.get())
            
            for i, item in enumerate(self.tree_cartas.get_children()):
                valores = self.tree_cartas.item(item)['values']
                if int(valores[0]) == id_busca:
                    self.tree_cartas.selection_set(item)
                    self.tree_cartas.focus(item)
                    self.tree_cartas.see(item)
                    self.selecionar_carta(None)
                    self.log(f"Carta ID {id_busca} encontrada")
                    return
            
            messagebox.showinfo("Não encontrado", f"Carta com ID {id_busca} não encontrada")
            
        except ValueError:
            messagebox.showerror("Erro", "Digite um ID válido")


def main():
    root = tk.Tk()
    app = InterfaceGrafica(root)
    root.mainloop()


if __name__ == "__main__":
    main()
