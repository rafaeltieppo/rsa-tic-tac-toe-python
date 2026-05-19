import socket

# =============================================================================
# MODULO 1 - FUNCOES RSA
# =============================================================================

def eh_primo(numero):
    if numero < 2:
        return False
    for divisor in range(2, numero):
        if numero % divisor == 0:
            return False
    return True

def listar_primos(inicio, fim):
    lista = []
    for x in range(inicio, fim):
        if eh_primo(x):
            lista.append(x)
    return lista

def maximo_divisor_comum(x, y):
    while y != 0:
        x, y = y, x % y
    return x

# =============================================================================
# MODULO 2 - GERACAO DAS CHAVES RSA
# =============================================================================

print("=" * 48)
print("  JOGADOR 2  |  JOGO DA VELHA COM RSA")
print("=" * 48)
print("\n[ Gerando par de chaves RSA ]\n")

print("Primos disponiveis (0 a 100):")
print(listar_primos(0, 100))
primo1 = int(input("Escolha o primeiro primo [p]: "))

print("\nPrimos disponiveis maiores que", primo1, ":")
print(listar_primos(primo1 + 1, 200))
primo2 = int(input("Escolha o segundo primo [q]: "))

modulo = primo1 * primo2
phi = (primo1 - 1) * (primo2 - 1)

print("\n  p   =", primo1)
print("  q   =", primo2)
print("  n   =", modulo)
print("  phi =", phi)

print("\nPrimos validos para E:")
print(listar_primos(primo2 + 1, phi))
expo_publico = int(input("Escolha o valor de E: "))

if maximo_divisor_comum(expo_publico, phi) != 1:
    print("Erro: mdc(E, phi) nao e 1.")
    expo_publico = int(input("Digite E novamente: "))

expo_privado = 1
resultado = 100
while resultado != 1:
    expo_privado = expo_privado + 1
    resultado = (expo_publico * expo_privado) % phi

print("\n  Chave Publica  -> [E=" + str(expo_publico) + ", n=" + str(modulo) + "]")
print("  Chave Privada  -> [D=" + str(expo_privado) + ", n=" + str(modulo) + "]")

# =============================================================================
# MODULO 3 - TABULEIRO
# =============================================================================

casas = [' '] * 9

def mostrar_tabuleiro():
    print("\n +---+---+---+")
    print(" | " + casas[0] + " | " + casas[1] + " | " + casas[2] + " |")
    print(" +---+---+---+")
    print(" | " + casas[3] + " | " + casas[4] + " | " + casas[5] + " |")
    print(" +---+---+---+")
    print(" | " + casas[6] + " | " + casas[7] + " | " + casas[8] + " |")
    print(" +---+---+---+\n")

def mostrar_legenda():
    print("\n Posicoes:")
    print(" +---+---+---+")
    print(" | 0 | 1 | 2 |")
    print(" +---+---+---+")
    print(" | 3 | 4 | 5 |")
    print(" +---+---+---+")
    print(" | 6 | 7 | 8 |")
    print(" +---+---+---+\n")

def tem_vitoria(simbolo):
    linhas_vencedoras = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    for linha in linhas_vencedoras:
        if casas[linha[0]] == casas[linha[1]] == casas[linha[2]] == simbolo:
            return True
    return False

def eh_empate():
    return ' ' not in casas

# =============================================================================
# MODULO 4 - CONEXAO TCP
# SOLUCAO: jogador 2 conecta no servidor do jogador 1 (porta 5000)
# um unico socket bidirecional — sem threading necessario
# =============================================================================

ip_j1 = input("\nIP do Jogador 1 (Enter = 127.0.0.1): ").strip()
if ip_j1 == '':
    ip_j1 = '127.0.0.1'

print("\n[Rede] Conectando ao Jogador 1...")
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# tenta conectar em loop ate o jogador 1 estar pronto
ok = False
while not ok:
    try:
        conn.connect((ip_j1, 5000))
        ok = True
    except:
        pass

print("[Rede] Conectado ao Jogador 1!")

# =============================================================================
# MODULO 5 - HANDSHAKE
# ORDEM: J2 recebe primeiro, depois envia
#        (espelho do jogador 1 que envia primeiro e recebe depois)
# =============================================================================

# jogador 2 RECEBE a chave do jogador 1 primeiro
msg_entrada = conn.recv(1024).decode()
campos = msg_entrada.split(":")
E_adv = int(campos[1])
n_adv = int(campos[2])
print("\n[Handshake] Chave do oponente recebida: [E=" + str(E_adv) + ", n=" + str(n_adv) + "]")

# jogador 2 ENVIA sua chave publica depois
msg_saida = "CHAVE:" + str(expo_publico) + ":" + str(modulo)
conn.send(msg_saida.encode())
print("[Handshake] Chave publica enviada.")
print("\n>>> Handshake OK! Jogo iniciando. <<<\n")

# =============================================================================
# MODULO 6 - PARTIDA
# =============================================================================

vez_j2 = False      # jogador 2 aguarda jogador 1 comecar
rodando = True

mostrar_legenda()

while rodando:
    mostrar_tabuleiro()

    if vez_j2:
        print("Sua vez! (O)")

        while True:
            try:
                posicao = int(input("Posicao (0 a 8): "))
                if posicao < 0 or posicao > 8:
                    print("Valor fora do intervalo.")
                elif casas[posicao] != ' ':
                    print("Casa ja ocupada.")
                else:
                    break
            except:
                print("Entrada invalida.")

        # cifra com chave privada: C = posicao^D mod n
        valor_cifrado = (posicao ** expo_privado) % modulo
        conn.send(("JOGADA:" + str(valor_cifrado)).encode())
        casas[posicao] = 'O'
        print("Jogou em", posicao, "| C =", valor_cifrado)

        if tem_vitoria('O'):
            mostrar_tabuleiro()
            print("VOCE VENCEU!")
            rodando = False
        elif eh_empate():
            mostrar_tabuleiro()
            print("EMPATE!")
            rodando = False
        else:
            vez_j2 = False

    else:
        print("Aguardando jogada do Jogador 1...")
        raw = conn.recv(1024).decode()
        C_recebido = int(raw.split(":")[1])

        # decifra com chave publica do adversario: M = C^E mod n
        M = (C_recebido ** E_adv) % n_adv
        print("Recebido C =", C_recebido, "| Posicao M =", M)

        if 0 <= M <= 8 and casas[M] == ' ':
            casas[M] = 'X'
        else:
            print("Jogada invalida!")
            rodando = False
            break

        if tem_vitoria('X'):
            mostrar_tabuleiro()
            print("Jogador 1 venceu.")
            rodando = False
        elif eh_empate():
            mostrar_tabuleiro()
            print("EMPATE!")
            rodando = False
        else:
            vez_j2 = True

# =============================================================================
# MODULO 7 - ENCERRAMENTO
# =============================================================================
print("\nJogo encerrado.")
conn.close()
