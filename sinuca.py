import pygame
import math
import random

# Inicialização do Pygame
pygame.init()

# Configurações da Tela
LARGURA, ALTURA = 800, 500
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Sinuca Divertida para Crianças")
relogio = pygame.time.Clock()

# Cores
VERDE_MESA = (34, 139, 34)
MARROM_BORDA = (139, 69, 19)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AMARELO = (255, 215, 0)
VERMELHO = (220, 20, 60)
AZUL = (30, 144, 255)

# Parâmetros físicos simples
A_ATRITO = 0.98  # Desaceleração das bolas

class Bola:
    def __init__(self, x, y, raio, cor, id_bola=0):
        self.x = x
        self.y = y
        self.raio = raio
        self.cor = cor
        self.vx = 0
        self.vy = 0
        self.id = id_bola

    def mover(self):
        self.x += self.vx
        self.y += self.vy
        # Aplicar atrito para as bolas pararem gradativamente
        self.vx *= A_ATRITO
        self.vy *= A_ATRITO
        
        # Parar completamente se estiver muito devagar
        if abs(self.vx) < 0.1: self.vx = 0
        if abs(self.vy) < 0.1: self.vy = 0

    def desenhar(self, superficie):
        pygame.draw.circle(superficie, self.cor, (int(self.x), int(self.y)), self.raio)
        # Detalhe de brilho na bola para parecer 3D simples
        pygame.draw.circle(superficie, BRANCO, (int(self.x - self.raio/3), int(self.y - self.raio/3)), int(self.raio/4))

# Criar caçapas (buracos) nas quinas e no meio
raio_cacapa = 25
cacapas = [
    (50, 50), (LARGURA//2, 45), (LARGURA-50, 50),
    (50, ALTURA-50), (LARGURA//2, ALTURA-45), (LARGURA-50, ALTURA-50)
]

# Inicializar Bolas
bola_branca = Bola(200, ALTURA // 2, 15, BRANCO, id_bola=1)
bolas = [bola_branca]

# Adicionar algumas bolas coloridas em forma de triângulo simples
cores_alvo = [VERMELHO, AMARELO, AZUL, VERMELHO, AMARELO]
start_x = 550
for i in range(3):
    for j in range(i + 1):
        bx = start_x + (i * 25)
        by = (ALTURA // 2) - (i * 15) + (j * 30)
        cor = random.choice(cores_alvo)
        bolas.append(Bola(bx, by, 15, cor))

# Variáveis de controle do jogo
clicando = False
ponto_inicio = (0, 0)
pontos_p1 = 0
pontos_p2 = 0
turno_p1 = True  # True = Jogador 1, False = Jogador 2

def verificar_colisoes():
    # Colisão com as bordas da mesa (considerando a madeira da borda)
    for b in bolas:
        if b.x - b.raio < 40:
            b.x = 40 + b.raio
            b.vx *= -1
        elif b.x + b.raio > LARGURA - 40:
            b.x = LARGURA - 40 - b.raio
            b.vx *= -1
            
        if b.y - b.raio < 40:
            b.y = 40 + b.raio
            b.vy *= -1
        elif b.y + b.raio > ALTURA - 40:
            b.y = ALTURA - 40 - b.raio
            b.vy *= -1

    # Colisão entre as bolas (Física elástica simples)
    for i in range(len(bolas)):
        for j in range(i + 1, len(bolas)):
            b1 = bolas[i]
            b2 = bolas[j]
            dx = b2.x - b1.x
            dy = b2.y - b1.y
            dist = math.hypot(dx, dy)
            
            if dist < (b1.raio + b2.raio):
                # Evitar que as bolas grudem
                overlap = (b1.raio + b2.raio) - dist
                if dist == 0: dist = 1 # evitar divisão por zero
                b1.x -= (dx / dist) * (overlap / 2)
                b1.y -= (dy / dist) * (overlap / 2)
                b2.x += (dx / dist) * (overlap / 2)
                b2.y += (dy / dist) * (overlap / 2)

                # Inverter as velocidades básicas no impacto
                b1.vx, b2.vx = b2.vx, b1.vx
                b1.vy, b2.vy = b2.vy, b1.vy

# Loop Principal do Jogo
rodando = True
while rodando:
    tela.fill(MARROM_BORDA)
    # Desenha o feltro verde da mesa
    pygame.draw.rect(tela, VERDE_MESA, (40, 40, LARGURA - 80, ALTURA - 80))
    
    # Desenha as caçapas
    for c in cacapas:
        pygame.draw.circle(tela, PRETO, c, raio_cacapa)

    # Eventos de entrada
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
            
        # Sistema de "Estilingue" com o mouse para chutar a bola branca
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            # Só permite chutar se clicar perto da bola branca e se as bolas estiverem paradas
            todas_paradas = all(b.vx == 0 and b.vy == 0 for b in bolas)
            if math.hypot(mx - bola_branca.x, my - bola_branca.y) < 30 and todas_paradas:
                clicando = True
                ponto_inicio = (bola_branca.x, bola_branca.y)
                
        elif evento.type == pygame.MOUSEBUTTONUP:
            if clicando:
                mx, my = pygame.mouse.get_pos()
                # Calcula a força baseada na distância que arrastou para trás
                dx = ponto_inicio[0] - mx
                dy = ponto_inicio[1] - my
                
                # Aplica a velocidade
                bola_branca.vx = dx * 0.15
                bola_branca.vy = dy * 0.15
                clicando = False
                
                # Alterna o turno das crianças após a tacada
                turno_p1 = not turno_p1

    # Atualizar e Desenhar Bolas
    for b in bolas[:]:
        b.mover()
        verificar_colisoes()
        
        # Verificar se entrou na caçapa
        for c in cacapas:
            if math.hypot(b.x - c[0], b.y - c[1]) < raio_cacapa:
                if b.id == 1:  # Se for a bola branca, ela volta para o início
                    b.x = 200
                    b.y = ALTURA // 2
                    b.vx = 0
                    b.vy = 0
                else:  # Se for colorida, pontua e some
                    bolas.remove(b)
                    if not turno_p1: # (Como o turno muda no clique, quem jogou foi o inverso)
                        pontos_p1 += 1
                    else:
                        pontos_p2 += 1

        b.desenhar(tela)

    # Desenhar linha de mira (Estilingue)
    if clicando:
        mx, my = pygame.mouse.get_pos()
        # Linha indicando para onde a bola vai
        dx = ponto_inicio[0] - mx
        dy = ponto_inicio[1] - my
        ponto_mira = (bola_branca.x + dx, bola_branca.y + dy)
        pygame.draw.line(tela, BRANCO, (bola_branca.x, bola_branca.y), ponto_mira, 3)

    # Interface de Texto (Placar e Turno)
    fonte = pygame.font.SysFont("Arial", 24, bold=True)
    
    texto_p1 = fonte.render(f"Crianca 1: {pontos_p1} pontos", True, BRANCO)
    texto_p2 = fonte.render(f"Crianca 2: {pontos_p2} pontos", True, BRANCO)
    
    str_turno = "Vez da Crianca 1" if turno_p1 else "Vez da Crianca 2"
    texto_turno = fonte.render(str_turno, True, AMARELO if turno_p1 else AZUL)

    tela.blit(texto_p1, (50, 10))
    tela.blit(texto_p2, (LARGURA - 250, 10))
    tela.blit(texto_turno, (LARGURA // 2 - 80, 10))

    # Tela de Fim de Jogo
    if len(bolas) == 1: # Só sobrou a branca
        fonte_fim = pygame.font.SysFont("Arial", 40, bold=True)
        vencedor = "Crianca 1 Venceu!" if pontos_p1 > pontos_p2 else "Crianca 2 Venceu!"
        if pontos_p1 == pontos_p2: vencedor = "Empate!"
        
        texto_fim = fonte_fim.render(vencedor, True, BRANCO)
        tela.blit(texto_fim, (LARGURA // 2 - 150, ALTURA // 2 - 20))

    pygame.display.flip()
    relogio.tick(60)

pygame.quit()