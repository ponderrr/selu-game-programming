import pygame

PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)  
GOLD = (255, 215, 0)  

pygame.init()

class Star:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.points = [
            (x, y-20),          # TOP OUTER POINT
            (x+6, y-8),         # TOP RIGHT INNER POINT
            (x+19, y-6),        # TOP RIGHT OUTER POINT
            (x+8, y+2),         # BOTTOM RIGHT INNER POINT
            (x+12, y+16),       # BOTTOM RIGHT OUTER POINT
            (x, y+8),           # BOTTOM INNER POINT
            (x-12, y+16),       # BOTTOM LEFT OUTER POINT
            (x-8, y+2),         # BOTTOM LEFT INNER POINT
            (x-19, y-6),        # TOP LEFT OUTER POINT
            (x-6, y-8),         # TOP LEFT INNER POINT
        ]
    
    def draw(self, screen):
        for i in range(len(self.points)):
            start = self.points[i]
            end = self.points[(i + 1) % len(self.points)]
            pygame.draw.line(screen, GOLD, start, end, 3)

screen = pygame.display.set_mode((1280, 720))

stars = []

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            new_star = Star(mouse_x, mouse_y)
            stars.append(new_star)
    
    screen.fill((255, 255, 255))
    
    # LETTERS A and P
    pygame.draw.line(screen, PURPLE, (400, 300), (500, 150), 8)             # LEFT
    pygame.draw.line(screen, PURPLE, (500, 150), (600, 300), 8)             # RIGHT        
    pygame.draw.line(screen, PURPLE, (450, 225), (550, 225), 8)             # HORIZONTAL
    
    pygame.draw.line(screen, PURPLE, (700, 150), (700, 300), 8)             # VERTICAL LINE
    pygame.draw.line(screen, PURPLE, (700, 150), (750, 150), 8)             # TOP HORIZONTAL
    pygame.draw.line(screen, PURPLE, (750, 150), (780, 180), 8)             # TOP RIGHT DIAGONAL
    pygame.draw.line(screen, PURPLE, (780, 180), (780, 220), 8)             # RIGHT VERTICAL
    pygame.draw.line(screen, PURPLE, (780, 220), (750, 250), 8)             # BOTTOM RIGHT DIAGONAL
    pygame.draw.line(screen, PURPLE, (750, 250), (700, 250), 8)             # BOTTOM HORIZONTAL
    
    # FOOTBALL
    pygame.draw.line(screen, BROWN, (500, 450), (600, 450), 8)              # TOP HORIZONTAL
    pygame.draw.line(screen, BROWN, (600, 450), (650, 500), 8)              # TOP RIGHT DIAGONAL
    pygame.draw.line(screen, BROWN, (650, 500), (650, 550), 8)              # RIGHT VERTICAL
    pygame.draw.line(screen, BROWN, (650, 550), (600, 600), 8)              # BOTTOM RIGHT DIAGONAL
    pygame.draw.line(screen, BROWN, (600, 600), (500, 600), 8)              # BOTTOM HORIZONTAL
    pygame.draw.line(screen, BROWN, (500, 600), (450, 550), 8)              # BOTTOM LEFT DIAGONAL
    pygame.draw.line(screen, BROWN, (450, 550), (450, 500), 8)              # LEFT VERTICAL
    pygame.draw.line(screen, BROWN, (450, 500), (500, 450), 8)              # TOP LEFT DIAGONAL
    pygame.draw.line(screen, BROWN, (500, 525), (600, 525), 8)              # MIDDLE HORIZONTAL
    pygame.draw.line(screen, BROWN, (520, 500), (520, 550), 4)              # LACE 1
    pygame.draw.line(screen, BROWN, (540, 495), (540, 555), 4)              # LACE 2
    pygame.draw.line(screen, BROWN, (560, 495), (560, 555), 4)              # LACE 3
    pygame.draw.line(screen, BROWN, (580, 500), (580, 550), 4)              # LACE 4
    
    for star in stars:
        star.draw(screen)
    
    pygame.display.flip()

pygame.quit()