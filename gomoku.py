from typing import List
import copy
import numpy
import pygame

pygame.init()

SCREEN_LENGTH = 774
screen = pygame.display.set_mode((SCREEN_LENGTH, SCREEN_LENGTH)) # 스크린
pygame.display.set_caption("오목") # 제목

background_img = pygame.image.load("img/checkerboard.png") # 배경 이미지

checkerboard = [] # 바둑판
for i in range(19):
    temp = []
    for j in range(19):
        temp.append(0)
    checkerboard.append(temp)

def extract_subcheckerboard(index):
    '''
    승자 확인을 위한 리스트 반환
    
    자세한 반환값
    =======
    1. index의 상하좌우 4개의 원소를 포함하는 9*9리스트

    2. 한 방향으로 4개이하의 원소가 있을 경우 그 방향의 최대 길이까지만 포함
    '''
    a = index[0]
    b = index[1]

    a_start = max(0, a - 4)
    a_end = min(19, a + 5)
    b_start = max(0, b - 4)
    b_end = min(19, b + 5)

    sub = [i[b_start:b_end] for i in checkerboard[a_start:a_end]]
    return sub

def check_winner(board, check_list):
    '''
    행 또는 열 또는 대각선으로 승리했는지 확인
    
    board에 어떠한 처리도 하지 않았다면 행을 확인하는 경우

    board에 전치(numpy.array.T)를 취했다면 열을 확인하는 경우

    all_square_list, diaginol을 거쳤다면 대각선을 확인하는 경우
    '''
    for i in board:
        for j in range(len(i) - 4):
            if i[j:j+5] == check_list:
                return True
    return False

def all_square_list(board):
    '''
    size*size 크기의 가능한 모든 리스트들을 리스트에 넣어 반환
    '''
    if len(board) == 0:
        return []

    row = len(board)
    column = len(board[0])

    if row == column:
        return [board]

    size = min(row, column)
    result = []

    for i in range(row - size + 1):
        for j in range(column - size + 1):
            sub = [k[j:j+size] for k in board[i:i+size]]
            result.append(sub)
    
    return result

def diagonal(board) -> List[List[int]]:
    '''
    대각선에 위치한 돌들의 리스트들을 result에 넣어 반환
    '''
    result = []

    copied_board1 = copy.deepcopy(board)
    for i in range(len(copied_board1) - 4):
        result.append(numpy.diag(numpy.array(copied_board1)).tolist())
        if len(copied_board1) == 5:
            break
        del copied_board1[0]
        for j in copied_board1:
            del j[-1]
    
    copied_board2 = copy.deepcopy(board)
    for i in range(len(copied_board2) - 4):
        result.append(numpy.diag(numpy.array(copied_board2)).tolist())
        if len(copied_board2) == 5:
            break
        del copied_board2[-1]
        for j in copied_board2:
            del j[0]
    
    return result

BLACKWINCHECK = [1, 1, 1, 1, 1] # 흑돌이 승리를 검사할 리스트
WHITEWINCHECK = [-1, -1, -1, -1, -1] # 백돌의 승리를 검사할 리스트

AREA_LENTH = 39
area = pygame.Surface((AREA_LENTH, AREA_LENTH), pygame.SRCALPHA) # 클릭시 착수 범위
area.fill((255, 255, 255, 0))

AREA_POS = 16 # 첫번째 area의 위치

poses = [] # area들의 위치를 담을 리스트
checkerboard_pos = [] # checkerboard의 위치를 담을 리스트
for i in range(19):
    for j in range(19):
        poses.append((AREA_POS + AREA_LENTH * j, AREA_POS + AREA_LENTH * i))
        checkerboard_pos.append((i, j))

rects = [] # area들의 rect를 담을 리스트
for i in range(361):
    rects.append(area.get_rect(topleft=poses[i]))

radius = 19 # 흑돌, 백돌의 반지름
circle_rect = None
circle = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

placement_poses = [] # 착수 위치를 담을 리스트
black = True # 흑돌 여부 (흑돌부터 시작)
running = True
while running:
    placement_pos = None
    subcheckerboard = []
    tempcheckerboard = []

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 클릭하면 돌 착수
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for i in range(361):
                if rects[i].collidepoint(mouse_pos):
                    pos = poses[i]
                    if black == True: # 흑돌 착수
                        placement_poses.append((pos[0] + radius, pos[1] + radius))
                        placement_pos = checkerboard_pos[i]
                        checkerboard[placement_pos[0]][placement_pos[1]] = 1 # 흑돌 위치 표시
                        subcheckerboard = extract_subcheckerboard(placement_pos) # 승자를 확인하기 위한 리스트 (placement_pos 주위 원소들)
                        # 대각선 돌들의 값을 tempcheckerboard에 넣기
                        for i in all_square_list(subcheckerboard):
                            tempcheckerboard += diagonal(i)
                        for i in all_square_list(list(reversed(subcheckerboard))):
                            tempcheckerboard += diagonal(i)
                        black = False
                    else: # 백돌 착수
                        placement_poses.append((pos[0] + radius, pos[1] + radius))
                        placement_pos = checkerboard_pos[i]
                        checkerboard[placement_pos[0]][placement_pos[1]] = -1 # 백돌 위치 표시
                        subcheckerboard = extract_subcheckerboard(placement_pos) # 승자를 확인하기 위한 리스트 (placement_pos 주위 원소들)
                        # 대각선 돌들의 값을 tempcheckerboard에 넣기
                        for i in all_square_list(subcheckerboard):
                            tempcheckerboard += diagonal(i)
                        for i in all_square_list(list(reversed(subcheckerboard))):
                            tempcheckerboard += diagonal(i)
                        black = True
        
    mouse_pos = pygame.mouse.get_pos()
    
    # 예상 착수 지점
    for i in rects:
        if i.collidepoint(mouse_pos):
            if black == True: # 흑돌의 예상 착수 지점
                circle_rect = i
                pygame.draw.circle(circle, (0, 0, 0, 128), (radius, radius), radius)
            else: # 백돌의 예상 착수 지점
                circle_rect = i
                pygame.draw.circle(circle, (255, 255, 255, 128), (radius, radius), radius)
    
    screen.blit(background_img, (0, 0))
    
    # 클릭시 착수 범위 지정
    for i in range(361):
        screen.blit(area, poses[i])
    
    # 예상 착수 지점 표시
    if circle_rect:
        screen.blit(circle, circle_rect)
    
    # 착수
    for i in range(len(placement_poses)):
        if i % 2 == 0: # 흑돌 착수
            pygame.draw.circle(screen, (0, 0, 0), placement_poses[i], radius)
        else: # 백돌 착수
            pygame.draw.circle(screen, (255, 255, 255), placement_poses[i], radius)
    
    # 승자 확인
    if black:
        win_by_row = check_winner(subcheckerboard, BLACKWINCHECK) # 행 확인
        win_by_column = check_winner(numpy.array(subcheckerboard).T.tolist(), BLACKWINCHECK) # 열 확인
        win_by_diagonal = check_winner(tempcheckerboard, BLACKWINCHECK) # 댁각선 확인
        if win_by_row or win_by_column or win_by_diagonal:
            print("Black win!")

    else:
        win_by_row = check_winner(subcheckerboard, WHITEWINCHECK) # 행 확인
        win_by_column = check_winner(numpy.array(subcheckerboard).T.tolist(), WHITEWINCHECK) # 열 확인
        win_by_diagonal = check_winner(tempcheckerboard, WHITEWINCHECK) # 대각선 확인
        if win_by_row or win_by_column or win_by_diagonal:
            print("White win!")
    
    pygame.display.flip()

pygame.quit()