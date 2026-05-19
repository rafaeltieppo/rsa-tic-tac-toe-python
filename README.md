🎮 Tic-Tac-Toe with RSA Asymmetric Cryptography
A distributed two-player Tic-Tac-Toe game over a local network, where every move is authenticated using RSA asymmetric cryptography — implemented from scratch in pure Python, with no external cryptographic libraries.

📌 About
This project was developed as an assignment for an Information Security course. The idea is to use Tic-Tac-Toe as a model for a distributed system where messages (moves) need to be authenticated — simulating the same principle behind digital signatures in real-world transactions.
Each move is encrypted with the sender's private key and decrypted by the opponent using the corresponding public key. Any tampering with the value during transmission is automatically detected at decryption.

🔐 How RSA works here

Each player picks two prime numbers p and q at startup
The program calculates n = p * q and φ(n) = (p-1) * (q-1)
The player picks E coprime to φ(n)
The program finds D such that (E * D) % φ(n) == 1
Public key: [E, n] → sent to the opponent
Private key: [D, n] → stays local

Move encryption:
C = position^D mod n
Verification by the opponent:
M = C^E_opponent mod n_opponent

🗂 Project structure
├── jogador1.py   # Player X — opens server on port 5000
├── jogador2.py   # Player O — connects to Player 1's server
└── README.md

▶️ How to run
Requirements

Python 3.x
No external libraries needed

Same machine (for testing)
Open two terminals side by side:
bash# Terminal 1
python jogador1.py

# Terminal 2
python jogador2.py
When asked for an IP address, just press Enter on both (defaults to 127.0.0.1).
Different machines on the same network
bash# Player 1's machine
python jogador1.py
# press Enter when asked for IP

# Player 2's machine
python jogador2.py
# type Player 1's local IP (e.g. 192.168.1.10)
To find Player 1's IP:

Windows: open CMD and type ipconfig
Linux/Mac: type ifconfig or ip a


🎯 Recommended primes
n must be greater than 8 (board positions range from 0 to 8).
pqnSuggested E5115577139111111718713
Both players can use different primes — each one generates their own key pair independently.

🖥️ Sample run
==================================================
   PLAYER 1 - TIC-TAC-TOE WITH RSA
==================================================

Available primes between 0 and 100:
[2, 3, 5, 7, 11, 13, ...]
Enter FIRST prime (p): 5
Enter SECOND prime (q): 11

N = 55 | Delta = 40
Enter value of E: 7

>>> PUBLIC KEY  : [E=7, n=55]
>>> PRIVATE KEY : [D=23, n=55]

[Handshake] Public key sent.
[Handshake] Opponent's key received: [E=11, n=91]

>>> Handshake complete! Game starting.

 Board positions:
 0 | 1 | 2
---+---+---
 3 | 4 | 5
---+---+---
 6 | 7 | 8

Your turn! (X)
Enter position (0-8): 4
Played at 4 | Encrypted value sent: C = 9

🛠 Tech stack

Python 3 — main language
socket — TCP/IP communication (Python standard library)
threading — parallelism on Player 1's side (Python standard library)
RSA — fully hand-rolled, no crypto libraries


📚 References

RIVEST, R. L.; SHAMIR, A.; ADLEMAN, L. A method for obtaining digital signatures and public-key cryptosystems. Communications of the ACM, 1978.
PYTHON SOFTWARE FOUNDATION. Socket programming HOWTO. Available at: https://docs.python.org/3/howto/sockets.html


👨‍💻 Author
Rafael Tieppo — Information Security
