import random
import socket
import json
import os
import time
import threading

Lock = threading.RLock()

ARQUIVO_PRODUTORES = 'BasedeDados/Produtores.json'
ARQUIVO_PRODUTOS = 'BasedeDados/Produtos.json'

conexoes = {}
produtos_comprados = []
threads_heartbeat = {}
taxas_revenda = {}

taxa_padrao = 20.0

def carregar_json(caminho_arquivo):
    """
    Carrega uma lista a partir de um arquivo JSON, se existir.
    """
    try:
        with open(caminho_arquivo, 'r') as f:
            conteudo = f.read() 
            return json.loads(conteudo)
    except FileNotFoundError:
        print(f"Arquivo {caminho_arquivo} não encontrado.")
        return []
    except json.JSONDecodeError:
        print(f"Erro ao decodificar o arquivo JSON {caminho_arquivo}.")
        return []

def gerar_categoria():
    """
    Seleciona aleatoriamente uma categoria de produtos.
    """
    produtos = carregar_json(ARQUIVO_PRODUTOS)
    todas_categorias = list(produtos.keys())
    return random.choice(todas_categorias) if todas_categorias else None
        
def testar_porta_ocupada(ip, porta):
    """
    Verifica se a porta está ocupada.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.01)
        try:
            s.bind((ip, porta))
            return False
        except socket.error:
            return True

def testar_conexoes():
    """
    Testa as conexões dos produtores e retorna aqueles que estão online.
    """
    produtores = carregar_json(ARQUIVO_PRODUTORES)
    return [
        (p["ID"], p["IP"], p["Porta"], p["Nome"])
        for p in produtores if testar_porta_ocupada(p["IP"], p["Porta"])
    ]

def listar_subscricoes():
    """
    Lista as subscrições de produtos comprados, separando por ID do produtor.
    """
    global taxa_padrao
    produtos_por_produtor = {}
    for id_produto, nome_produtor, ip, porta, nome_produto, quantidade, preco_compra in produtos_comprados:
        if id_produto not in produtos_por_produtor:
            produtos_por_produtor[id_produto] = {
                "nome": nome_produtor,
                "ip": ip,
                "porta": porta,
                "produtos": []
            }
        taxa_revenda = taxas_revenda.get(nome_produto, taxa_padrao)
        preco_venda = preco_compra + (preco_compra * taxa_revenda / 100)
        produtos_por_produtor[id_produto]["produtos"].append((nome_produto, quantidade, preco_compra, taxa_revenda, preco_venda))
    for id_produtor, detalhes in produtos_por_produtor.items():
        print(f"Produtor: {detalhes['nome']} (ID: {id_produtor}, IP: {detalhes['ip']}, Porta: {detalhes['porta']})")
        for nome_produto, quantidade, preco_compra, taxa_revenda, preco_venda in detalhes["produtos"]:
            print(f"  - Nome: {nome_produto}, Quantidade: {quantidade}, Preço de Compra: {preco_compra:.2f}, Preço de Venda: {preco_venda:.2f} ({taxa_revenda}%)")

def definir_taxa_revenda():
    """
    Permite definir uma taxa de revenda para os produtos já comprados.
    """
    if not produtos_comprados:
        print("Nenhum produto foi comprado ainda.")
        return
    print("Produtos comprados disponíveis para revenda:")
    for i, (id_produtor, nome_produtor, ip, porta, nome_produto, quantidade, preco_compra) in enumerate(produtos_comprados, 1):
        taxa_atual = taxas_revenda.get(nome_produto, 0)
        print(f"{i}. {nome_produto} - Quantidade: {quantidade}, Taxa de Revenda Atual: {taxa_atual}% (Produtor: {nome_produtor})")
    try:
        escolha = int(input("\nEscolha o número do produto para definir a taxa de revenda: "))
        produto_escolhido = produtos_comprados[escolha - 1]
        taxa = float(input(f"Digite a taxa de revenda para o produto {produto_escolhido[4]} (em %): "))
        if taxa < 0:
            print("A taxa não pode ser negativa.")
            return
        taxas_revenda[produto_escolhido[4]] = taxa
        print(f"Taxa de revenda de {taxa}% definida para o produto {produto_escolhido[4]}.")
    except (ValueError, IndexError):
        print("Seleção inválida. Tente novamente.")

def comprar_produtos():
    """
    Gerencia a compra de produtos.
    """
    produtos = carregar_json(ARQUIVO_PRODUTOS)
    todas_categorias = list(produtos.keys())
    if not todas_categorias:
        print("Nenhuma categoria disponível.")
        return
    print("Categorias disponíveis:")
    for categoria in todas_categorias:
        print(f"- {categoria}")
    while True:
        categoria = input("Escolha uma Categoria (ou digite 0 para voltar): ")
        if categoria == '0':
            print("Voltando ao menu anterior.")
            return  
        if categoria in todas_categorias:
            if menu_pesquisa_produtos(categoria) != 1:
                break
            else:
                print(f"Nenhum produto disponivel na categoria {categoria}. Tente novamente.")
        else:
            print("Categoria inválida. Tente novamente.")

def conectar_ao_produtor(sock_antigo, ip, porta, nome_produtor):
    """
    Tenta se conectar ao produtor e retorna o socket.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, porta))
        conexoes[(ip, porta)] = (sock, nome_produtor)
        return sock
    except socket.error:
        return sock_antigo

def verificar_conexao_periodicamente(sock, ip, porta, nome_produtor, timeout=30):
    """
    Verifica periodicamente a conexão com o produtor.
    """
    falhas_consec = 0
    while falhas_consec * 2 < timeout:
        with Lock:
            try:
                sock.sendall(b"HEARTBEAT")
                resposta = sock.recv(1024).decode('utf-8')
                if resposta != "OK":
                    raise socket.error("Resposta inesperada do produtor")
                falhas_consec = 0
            except socket.error:
                falhas_consec += 1
                print(f"Perda de conexão com o produtor {nome_produtor} ({ip}:{porta}) - tentativa {falhas_consec}")
                novo_sock = conectar_ao_produtor(sock, ip, porta, nome_produtor)
                if novo_sock and novo_sock != sock:
                    print(f"Conexão restabelecida com o produtor {nome_produtor} ({ip}:{porta})")
                    sock.close()
                    sock = novo_sock
                    conexoes[(ip, porta)] = (sock, nome_produtor)
        time.sleep(2)
    print(f"Produtor {nome_produtor} ({ip}:{porta}) desconectado por mais de {timeout} segundos. Removendo produtos.")
    remover_produtos_produtor(nome_produtor, ip, porta)
    return False

def remover_produtos_produtor(nome_produtor, ip, porta):
    """
    Remove todos os produtos de um produtor desconectado.
    """
    global produtos_comprados
    global conexoes
    produtos_comprados = [p for p in produtos_comprados if p[0] != nome_produtor]
    if (ip, porta) in conexoes:
        sock, _ = conexoes[(ip, porta)]
        sock.close()
        del conexoes[(ip, porta)]
    print(f"Todos os produtos do produtor {nome_produtor} foram removidos.")

def menu_pesquisa_produtos(categoria_desejada):
    global conexoes
    global produtos_comprados
    global taxa_padrao
    produtores_ativos = testar_conexoes()
    produtos_lista = []
    for _, ip, porta, nome_produtor in produtores_ativos:
        sock_info = conexoes.get((ip, porta))
        if sock_info is None:
            sock = conectar_ao_produtor(None, ip, porta, nome_produtor)
            if sock is None:
                continue
            thread_heartbeat = threading.Thread(target=verificar_conexao_periodicamente, args=(sock, ip, porta, nome_produtor))
            thread_heartbeat.daemon = True
            thread_heartbeat.start()
            threads_heartbeat[(ip, porta)] = thread_heartbeat
        else:
            sock = sock_info[0]
        try:
            with Lock:
                sock.sendall(b"LISTAR_PRODUTOS")
                produtos = sock.recv(4096).decode('utf-8')
            produtos_filtrados = [
                linha for linha in produtos.splitlines()
                if linha.partition(' - ')[2].split('Categoria: ')[1].split(' - ')[0] == categoria_desejada
                and int(linha.partition('Quantidade: ')[2]) > 0
            ]
            for produto in produtos_filtrados:
                produtos_lista.append((nome_produtor, ip, porta, produto))
        except socket.error as e:
            print(f"Erro ao solicitar produtos de {nome_produtor} ({ip}:{porta}): {e}")
            sock.close()
            conexoes.pop((ip, porta), None)
    if not produtos_lista:
        return 1
    print(f"\nCategoria: {categoria_desejada}")
    print("\nLista de produtos disponíveis:")
    produtor_anterior = None
    for i, (nome_produtor, ip, porta, produto) in enumerate(produtos_lista, 1):
        if nome_produtor != produtor_anterior:
            print(f"Produtor: {nome_produtor} (IP: {ip}, Porta: {porta})")
            produtor_anterior = nome_produtor
        print(f"{i}. {produto}")
    escolhas = input("\nEscolha os números dos produtos que deseja comprar (separados por vírgula): ")
    try:
        escolhas_validas = [produtos_lista[int(num.strip()) - 1] for num in escolhas.split(',') if num.strip().isdigit()]
        for nome_produtor, ip, porta, produto in escolhas_validas:
            sock = conexoes[(ip, porta)][0]
            nome_produto = produto.split(' - ')[0]
            preco_compra = float(produto.split('Preço: ')[1].split(' - ')[0])
            id_produtor = next(p[0] for p in testar_conexoes() if p[1] == ip and p[2] == porta)
            while True:
                quantidade = input(f"Digite a quantidade para {nome_produto}: ")
                with Lock:
                    mensagem_compra = f"SUBSCREVER_PRODUTO,{nome_produto},{quantidade}"
                    sock.sendall(mensagem_compra.encode('utf-8'))
                    resposta = sock.recv(1024).decode('utf-8')
                if resposta == "Produto não encontrado ou quantidade insuficiente.":
                    print(resposta)
                else:
                    produtos_comprados.append((id_produtor, nome_produtor, ip, porta, nome_produto, quantidade, preco_compra))
                    taxas_revenda[nome_produto] = taxa_padrao 
                    print(f"Compra confirmada com taxa de revenda padrão de 20% para {nome_produto}.")
                    break
    except (ValueError, IndexError):
        print("Seleção inválida. Tente novamente com números válidos.")

def menu_marketplace():
    """
    Apresenta o menu principal do marketplace.
    """
    while True:
        print("--- Menu Marketplace ---")
        print("1. Lista de Subscrições")
        print("2. Comprar Produtos")
        print("3. Definir Taxa de Revenda")
        print("99. Sair")
        escolha = input("Escolha uma opção: ")
        if escolha == '1':
            listar_subscricoes()
        elif escolha == '2':
            comprar_produtos()
        elif escolha == '3':
            definir_taxa_revenda()
        elif escolha == '99':
            print("Saindo do Marketplace. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

def iniciar():
    """
    Inicia o marketplace e gerencia as conexões.
    """
    while True:
        categoria = gerar_categoria()
        if menu_pesquisa_produtos(categoria) != 1:
            break
    menu_marketplace()
    for sock, _ in conexoes.values():
        sock.close()
    print("Conexões fechadas.")

if __name__ == "__main__":
    iniciar()