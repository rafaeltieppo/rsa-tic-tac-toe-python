import socket
import threading

# =============================================================================
# BLOCO 1 - FUNCOES RSA
# =============================================================================

def primo(n):
    if n == 1:
        return 0
    if n == 2:
        return 1
    for i in range(2, n):
        if (n % i) == 0:
            return 0
    return 1

def gerarPrimo(inicio, fim):
    aux = []
    for i in range(inicio, fim):
        if primo(i) == 1:
            aux.append(i)
    return aux

def mdc(a, b):
    while b != 0:
        a, b = b, a % b
    return a

# =============================================================================
# BLOCO 2 - GERACAO DAS CHAVES RSA
# =============================================================================

print("=" * 50)
print("   JOGADOR 1 - JOGO DA VELHA COM RSA")
print("=" * 50)
print("\n--- GERACAO DAS CHAVES RSA ---")

print("\nPrimos disponiveis entre 0 e 100:")
print(gerarPrimo(0, 100))
p = int(input("Digite o PRIMEIRO primo (p): "))

print("\nPrimos disponiveis maiores que p:")
print(gerarPrimo(p + 1, 200))
q = int(input("Digite o SEGUNDO primo (q): "))

n = p * q
delta = (p - 1) * (q - 1)

print("\nP =", p)
print("Q =", q)
print("N =", n)
print("Delta =", delta)

print("\nPrimos disponiveis para E:")
print(gerarPrimo(q + 1, delta))
E = int(input("Digite o valor de E: "))

if mdc(E, delta) != 1:
    print("ATENCAO: mdc(E, delta) nao e 1! Escolha outro E.")
    E = int(input("Digite E novamente: "))

D = 1
flag = 100
while flag != 1:
    D = D + 1
    flag = (E * D) % delta

print("\n>>> CHAVE PUBLICA  : [E=" + str(E) + ", n=" + str(n) + "]")
print(">>> CHAVE PRIVADA  : [D=" + str(D) + ", n=" + str(n) + "]")

# =============================================================================
# BLOCO 3 - TABULEIRO
# =============================================================================

tabuleiro = [' '] * 9

def exibir_tabuleiro():
    print("\n Tabuleiro:")
    print(" " + tabuleiro[0] + " | " + tabuleiro[1] + " | " + tabuleiro[2])
    print("---+---+---")
    print(" " + tabuleiro[3] + " | " + tabuleiro[4] + " | " + tabuleiro[5])
    print("---+---+---")
    print(" " + tabuleiro[6] + " | " + tabuleiro[7] + " | " + tabuleiro[8])
    print("")

def exibir_posicoes():
    print("\n Posicoes:")
    print(" 0 | 1 | 2")
    print("---+---+---")
    print(" 3 | 4 | 5")
    print("---+---+---")
    print(" 6 | 7 | 8\n")

def verificar_vitoria(simbolo):
    combinacoes = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    for combo in combinacoes:
        if tabuleiro[combo[0]] == tabuleiro[combo[1]] == tabuleiro[combo[2]] == simbolo:
            return True
    return False

def verificar_empate():
    return ' ' not in tabuleiro

# =============================================================================
# BLOCO 4 - CONEXAO TCP
# SOLUCAO: jogador 1 abre servidor, jogador 2 conecta nele
# um unico socket bidirecional para toda a comunicacao
# =============================================================================

ip_oponente = input("\nDigite o IP do Jogador 2 (Enter para 127.0.0.1): ").strip()
if ip_oponente == '':
    ip_oponente = '127.0.0.1'

# jogador 1 abre servidor na porta 5000 e aguarda jogador 2 conectar
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind(('0.0.0.0', 5000))
servidor.listen(1)
print("\n[Rede] Aguardando conexao do Jogador 2 na porta 5000...")
conn, endereco = servidor.accept()  # conn e o socket para falar com o jogador 2
print("[Rede] Jogador 2 conectado de", endereco)

# =============================================================================
# BLOCO 5 - HANDSHAKE: TROCA DE CHAVES
# ORDEM: J1 envia primeiro, depois recebe
#        J2 recebe primeiro, depois envia
# isso evita o deadlock onde os dois ficam esperando ao mesmo tempo
# =============================================================================

# jogador 1 ENVIA a chave publica primeiro
mensagem_chave = "CHAVE:" + str(E) + ":" + str(n)
conn.send(mensagem_chave.encode())
print("\n[Handshake] Chave publica enviada.")

# jogador 1 RECEBE a chave publica do jogador 2
dados = conn.recv(1024).decode()
partes = dados.split(":")
E_op = int(partes[1])
n_op = int(partes[2])
print("[Handshake] Chave do oponente recebida: [E=" + str(E_op) + ", n=" + str(n_op) + "]")
print("\n>>> Handshake OK! Jogo iniciando. <<<")

# =============================================================================
# BLOCO 6 - LOOP DO JOGO
# =============================================================================

minha_vez = True
jogo_ativo = True

exibir_posicoes()

while jogo_ativo:
    exibir_tabuleiro()

    if minha_vez:
        print("Sua vez! (X)")

        while True:
            try:
                pos = int(input("Digite a posicao (0-8): "))
                if pos < 0 or pos > 8:
                    print("Posicao invalida.")
                elif tabuleiro[pos] != ' ':
                    print("Posicao ocupada.")
                else:
                    break
            except:
                print("Digite apenas numeros.")

        # cifra com chave privada: C = pos^D mod n
        C = (pos ** D) % n
        conn.send(("JOGADA:" + str(C)).encode())
        tabuleiro[pos] = 'X'
        print("Jogou em", pos, "| C =", C)

        if verificar_vitoria('X'):
            exibir_tabuleiro()
            print("VOCE VENCEU!")
            jogo_ativo = False
        elif verificar_empate():
            exibir_tabuleiro()
            print("EMPATE!")
            jogo_ativo = False
        else:
            minha_vez = False

    else:
        print("Aguardando jogada do Jogador 2...")
        dados = conn.recv(1024).decode()
        partes = dados.split(":")
        C_recebido = int(partes[1])

        # decifra com chave publica do oponente: M = C^E mod n
        M = (C_recebido ** E_op) % n_op
        print("Recebido C =", C_recebido, "| Posicao decifrada M =", M)

        if 0 <= M <= 8 and tabuleiro[M] == ' ':
            tabuleiro[M] = 'O'
        else:
            print("Jogada invalida!")
            jogo_ativo = False
            break

        if verificar_vitoria('O'):
            exibir_tabuleiro()
            print("Jogador 2 venceu.")
            jogo_ativo = False
        elif verificar_empate():
            exibir_tabuleiro()
            print("EMPATE!")
            jogo_ativo = False
        else:
            minha_vez = True

# =============================================================================
# BLOCO 7 - ENCERRAMENTO
# =============================================================================
print("\nJogo encerrado.")
conn.close()
servidor.close()
