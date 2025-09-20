import socket
import random
import json
import threading
import os
import time
import psutil

Lock = threading.RLock()

IP = '127.0.0.1'
Porta_Default = 1025

servidor_ativo = True
arquivo_produtores = 'BasedeDados/Produtores.json'
arquivo_produtos = 'BasedeDados/Produtos.json'

CATEGORIAS_PERMITIDAS = ["Fruta", "Livros", "Roupa", "Ferramentas", "Computadores", "Smartphones", "Filmes", "Sapatos"]

COR_SUCESSO = '\033[92m' 
COR_ERRO = '\033[91m'    
COR_RESET = '\033[0m'  

def carregar_dados(arquivo):
    with Lock:
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

def salvar_dados(arquivo, dados):
    with Lock:
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

def gerar_id_ou_porta_socket(lista, chave, valor_default):
    valores = [int(item[chave]) for item in lista if item.get(chave) and str(item[chave]).isdigit()]
    return max(valores) + 1 if valores else valor_default

def registar_produtor(nome_produtor, IP_Default):
    produtores = carregar_dados(arquivo_produtores)
    id_produtor = gerar_id_ou_porta_socket(produtores, 'ID', 1)
    porta_socket = gerar_id_ou_porta_socket(produtores, 'Porta', Porta_Default)
    novo_produtor = {"ID": id_produtor, "Nome": nome_produtor, "IP": IP_Default, "Porta": porta_socket, "Produtos": []}
    produtores.append(novo_produtor)
    salvar_dados(arquivo_produtores, produtores)
    print(f"Produtor '{nome_produtor}' registrado com ID {id_produtor} e Porta {porta_socket}.")
    return id_produtor, porta_socket

def gerar_itens_para_produtor_socket(id_produtor, numero_itens):   
    produtos = carregar_dados(arquivo_produtos)
    produtores = carregar_dados(arquivo_produtores)
    todos_produtos = [dict(produto, Categoria=categoria) for categoria, lista_produtos in produtos.items() for produto in lista_produtos]
    produtos_selecionados = random.sample(todos_produtos, min(numero_itens, len(todos_produtos)))
    produtor = next((p for p in produtores if p['ID'] == id_produtor), None)
    with Lock:
        for produto in produtos_selecionados:
            item_gerado = {
                "produto": produto['Nome_Produto'],
                "categoria": produto['Categoria'],
                "preco": round(random.uniform(produto['Preco'][0], produto['Preco'][1]), 2),  
                "quantidade": random.randint(produto['Quantidade'][0], produto['Quantidade'][1]) 
            }
            produtor['Produtos'].append(item_gerado)
        salvar_dados(arquivo_produtores, produtores)
    print(f"{numero_itens} itens gerados.")


def listar_produtos_socket(produtos):
    return [f"{produto['Nome']} - Categoria: {produto.get('Categoria', 'Desconhecida')} - Preço: {produto['Preco']:.2f} - Quantidade: {produto['Quantidade']}" for produto in produtos]

def adicionar_stock_periodicamente(id_produtor):
    intervalo_tempo = 60
    while True:
        time.sleep(intervalo_tempo)
        produtores = carregar_dados(arquivo_produtores)
        produtor = next((p for p in produtores if p["ID"] == id_produtor), None)
        if produtor and produtor['Produtos']:
            num_produtos_para_atualizar = random.randint(1, len(produtor['Produtos']))
            produtos_para_atualizar = random.sample(produtor['Produtos'], num_produtos_para_atualizar)
            with Lock:
                for produto in produtos_para_atualizar:
                    stock_atual = produto.get('quantidade', 0)
                    quantidade_maxima = random.randint(100, 200)
                    novo_stock = min(stock_atual + random.randint(5, 20), quantidade_maxima)
                    produto['quantidade'] = novo_stock
                    print(f"Stock de '{produto['produto']}' atualizado para {novo_stock} [Antigo: {stock_atual}].")     
            salvar_dados(arquivo_produtores, produtores)

def listar_produtos_endpoint(cliente_socket, id_produtor):
    produtores = carregar_dados(arquivo_produtores)
    produtor = next((p for p in produtores if p['ID'] == id_produtor), None)
    produtos = produtor['Produtos'] if produtor else []
    resposta = "\n".join(listar_produtos_socket(produtos)) if produtos else "Nenhum produto disponível."
    cliente_socket.sendall(resposta.encode())

def comprar_produto_endpoint(cliente_socket, id_produtor, nome_produto, quantidade):
    produtores = carregar_dados(arquivo_produtores)
    produtor = next((p for p in produtores if p['ID'] == id_produtor), None)
    with Lock:
        produto_info = next((prod for prod in produtor['Produtos'] if prod['produto'] == nome_produto), None)
        if produto_info and produto_info['quantidade'] >= quantidade:
            produto_info['quantidade'] -= quantidade
            salvar_dados(arquivo_produtores, produtores)
            resposta = "OK"
            print(f"Cliente comprou {quantidade} de '{nome_produto}'.")
        else:
            resposta = "Produto não encontrado ou quantidade insuficiente."
            print(f"Compra falhou: Produto '{nome_produto}' não encontrado ou quantidade insuficiente.")
    cliente_socket.sendall(resposta.encode())

def listar_categorias(cliente_socket, id_produtor):
    produtores = carregar_dados(arquivo_produtores)
    produtor = next((p for p in produtores if p['ID'] == id_produtor), None)
    if produtor:
        categorias = set()
        for produto in produtor['Produtos']:
            categorias.add(produto['categoria'])
        categorias = list(categorias)
        if categorias:
            resposta = "Categorias disponíveis:\n" + "\n".join(categorias)
        else:
            resposta = "Nenhuma categoria disponível."
    else:
        resposta = f"Produtor com ID {id_produtor} não encontrado."
    cliente_socket.sendall(resposta.encode('utf-8'))

def listar_produtos_por_categoria(cliente_socket, id_produtor, categoria):
    try:
        with open('BasedeDados/Produtores.json', 'r') as file:
            produtores = json.load(file)
        produtor = next((p for p in produtores if p['ID'] == id_produtor), None)
        if produtor:
            produtos_encontrados = []
            for produto in produtor['Produtos']:
                if produto['categoria'].strip().lower() == categoria.strip().lower():
                    produto_info = {
                        "categoria": produto['categoria'],
                        "produto": produto['produto'],
                        "quantidade": produto['quantidade'],
                        "preco": f"{produto['preco']}"
                    }
                    produtos_encontrados.append(produto_info)
            if produtos_encontrados:
                resposta = json.dumps(produtos_encontrados, ensure_ascii=False)
            else:
                resposta = json.dumps({"erro": f"Não há produtos na categoria {categoria} para o produtor {id_produtor}."}, ensure_ascii=False)
        else:
            resposta = json.dumps({"erro": f"Produtor com ID {id_produtor} não encontrado."}, ensure_ascii=False)
        cliente_socket.sendall(resposta.encode('utf-8'))
    except Exception as e:
        print(f"Erro ao listar produtos por categoria: {e}")
        cliente_socket.sendall(f"Erro ao listar produtos: {e}".encode('utf-8'))

def gerenciar_conexao(cliente_socket, endereco, conexoes, produtos_marketplace, id_produtor):
    try:
        print(f"Conexão estabelecida com {endereco}.")
        with cliente_socket:
            while True:
                data = cliente_socket.recv(1024).decode()
                if not data:
                    break
                print(f"Mensagem recebida: {data}")
                if data.startswith("LISTAR_PRODUTOS_CATEGORIA"):
                    try:
                        _, categoria = data.split(",", maxsplit=1)
                        print(f"Listar produtos na categoria: {categoria.strip()}")
                        listar_produtos_por_categoria(cliente_socket, id_produtor, categoria.strip())
                    except Exception as e:
                        print(f"Erro ao processar LISTAR_PRODUTOS_CATEGORIA: {e}")
                else:
                    if data.startswith("SUBSCREVER_PRODUTO"):
                        try:
                            _, nome_produto, quantidade = data.split(',', maxsplit=2)
                            quantidade = int(quantidade.strip())
                            produtos_marketplace.setdefault(endereco, []).append((nome_produto.strip(), quantidade))
                            comprar_produto_endpoint(cliente_socket, id_produtor, nome_produto.strip(), quantidade)
                        except Exception as e:
                            print(f"Erro ao processar SUBSCREVER_PRODUTO: {e}")
                    elif data.startswith("LISTAR_PRODUTOS"):
                        listar_produtos_endpoint(cliente_socket, id_produtor)
                    elif data.startswith("HEARTBEAT"):
                        cliente_socket.sendall("OK".encode('utf-8'))
                    elif data.startswith("LISTAR_CATEGORIAS"):
                        listar_categorias(cliente_socket, id_produtor)     
    except Exception as e:
        print(f"Erro na conexão com {endereco}: {e}")
    finally:
        print(f"Conexão encerrada com {endereco}.")
        cliente_socket.close()

def servidor_produtor(nome_produtor, id_produtor, porta, ip):
    global servidor_ativo
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.bind(('', porta))
    servidor_socket.listen(5)
    print(f"Servidor do Produtor '{nome_produtor}' iniciado no IP {ip} e porta {porta}.")
    conexoes = []
    produtos_marketplace = {}
    threading.Thread(target=adicionar_stock_periodicamente, args=(id_produtor,)).start()
    while servidor_ativo:
        try:
            servidor_socket.settimeout(1.0)
            try:
                cliente_socket, endereco = servidor_socket.accept()
            except socket.timeout:
                continue
            threading.Thread(target=gerenciar_conexao, args=(cliente_socket, endereco, conexoes, produtos_marketplace, id_produtor)).start()
        except OSError:
            break
    servidor_socket.close()
    print(f"Servidor do Produtor '{nome_produtor}' desligado.")

def iniciar_sessao_produtor():
    nome_produtor = input("Digite o nome do produtor: ")
    id_produtor = input("Digite o ID do produtor: ")
    produtores = carregar_dados(arquivo_produtores)
    produtor = next((p for p in produtores if p['Nome'] == nome_produtor and str(p['ID']) == id_produtor), None)
    if produtor:
        print(f"Bem-vindo de volta, {produtor['Nome']}!")
        return produtor['Nome'], produtor['ID'], produtor['Porta'], produtor['IP']
    else:
        print("Produtor não encontrado.")
        return None, None, None

def menu_inicial(IP_Default):
    while True:
        opcao = input("\n--- Menu Inicial ---\n1. Criar novo produtor\n2. Iniciar sessão com produtor existente\n99. Sair\nEscolha uma opção: ")
        if opcao == '1':
            nome_produtor = input("Digite o nome do novo produtor: ")
            id_produtor, porta = registar_produtor(nome_produtor, IP_Default)
            gerar_itens_para_produtor_socket(id_produtor, random.randint(3, 5))
            servidor_produtor(nome_produtor, id_produtor, porta, IP_Default)
            break
        elif opcao == '2':
            nome_produtor, id_produtor, porta, ip = iniciar_sessao_produtor()
            if nome_produtor and id_produtor:
                servidor_produtor(nome_produtor, id_produtor, porta, ip)
            break
        elif opcao == '99':
            print("Saindo...")
            break

def obter_ip_vpn():
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address.startswith('10.'):
                return addr.address
    return None

if __name__ == "__main__":
    IP_Default = obter_ip_vpn()
    if IP_Default:
        print(f"{COR_SUCESSO}Sucesso: {COR_RESET}IP VPN detectado: {IP_Default}")
        menu_inicial(IP_Default)
    else:
        print(f"{COR_ERRO}Erro: {COR_RESET}IP VPN não detectado, tente outra vez!")