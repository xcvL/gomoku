from typing import List, Tuple
import copy
import numpy
import pygame

# ========== functions ==========

def all_square_list(board: List[List[int]]) -> List[List[List[int]]]:
    '''
    `size` * `size` 크기의 가능한 모든 리스트들을 리스트에 넣어 반환
    
    :param board: `subcheckerboard`
    :type board: List[List[int]]
    :return: `size` * `size` 크기의 가능한 모든 리스트들을 넣은 리스트
    :rtype: List[List[List[int]]]
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

def diagonal(board: List[List[int]]) -> List[List[int]]:
    '''
    대각선 돌들의 값을 넣은 리스트들을 넣은 리스트를 반환
    
    :param board: `subcheckerboard`
    :type board: List[List[int]]
    :return: 대각선 돌들의 값을 넣은 리스트들을 넣은 리스트
    :rtype: List[List[int]]
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

def check_winner(board: List[List[int]], check_list: List) -> bool:
    '''
    행 또는 열 또는 대각선으로 승리했는지 확인
    
    :param board: `subcheckerboard`
    :type board: List[List[int]]
    :param check_list: 오목 완성 확인 리스트
    :type check_list: List
    :return: 오목을 완성 했다면 True, 아니라면 False
    :rtype: bool
    '''

    for i in board:
        for j in range(len(i) - 4):
            if i[j:j+5] == check_list:
                return True
    return False

def winner(placement_pos: Tuple[int, int], check_list: List[int]) -> bool:
    '''
    오목 완성 확인
    
    :param placement_pos: 착수 지점
    :type placement_pos: Tuple[int, int]
    :param check_list: 오목 완성 확인 리스트
    :type check_list: List[int]
    :return: 오목이 완성 되었다면 True, 아니라면 False
    :rtype: bool
    '''

    tempboard = []
    x = placement_pos[0]
    y = placement_pos[1]

    a_start = max(0, x - 4)
    a_end = min(19, x + 5)
    b_start = max(0, y - 4)
    b_end = min(19, y + 5)

    subcheckerboard = [i[b_start:b_end] for i in checkerboard[a_start:a_end]]

    # 대각선 돌들의 값을 tempboard에 넣기
    for i in all_square_list(subcheckerboard):
        tempboard += diagonal(i)
    for i in all_square_list(list(reversed(subcheckerboard))):
        tempboard += diagonal(i)
                        
    win_by_row = check_winner(subcheckerboard, check_list) # 행 확인
    win_by_column = check_winner(numpy.array(subcheckerboard).T.tolist(), check_list) # 열 확인
    win_by_diagonal = check_winner(tempboard, check_list) # 댁각선 확인

    return win_by_row or win_by_column or win_by_diagonal

# ========== end ==========

pygame.init()

SCREEN_LENGTH = 774
screen = pygame.display.set_mode((SCREEN_LENGTH, SCREEN_LENGTH)) # 스크린
pygame.display.set_caption("오목") # 제목

background_img = pygame.image.load("img/checkerboard.png") # 배경 이미지

font = pygame.font.SysFont(None, 150)# 폰트
TEXT_COLOR = (3, 34, 171) # 텍스트 색상

checkerboard = [] # 바둑판
for i in range(19):
    temp = []
    for j in range(19):
        temp.append(0)
    checkerboard.append(temp)

# 오목 완성 확인 리스트
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

RADIUS = 19 # 흑돌, 백돌의 반지름
circle_rect = None
circle = pygame.Surface((RADIUS * 2, RADIUS * 2), pygame.SRCALPHA)

placement_poses = [] # 착수 위치를 담을 리스트
black = True # 흑돌 여부 (흑돌부터 시작)
show_text = False # 텍스트 렌더링 여부
end = False # 종료 여부
running = True
while running:
    subcheckerboard = []
    tempcheckerboard = []

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]: # 초기화
            placement_poses = []
            black = True
            show_text = False
            end = False
            checkerboard = [] # 바둑판
            for i in range(19):
                temp = []
                for j in range(19):
                    temp.append(0)
                checkerboard.append(temp)
        
        # 클릭하면 돌 착수
        if event.type == pygame.MOUSEBUTTONDOWN and not end:
            mouse_pos = event.pos
            for i in range(361):
                if rects[i].collidepoint(mouse_pos):
                    pos = poses[i]
                    placement_pos = checkerboard_pos[i]
                    stone_value = checkerboard[placement_pos[0]][placement_pos[1]]

                    if black and stone_value == 0: # 흑돌 착수
                        placement_poses.append((pos[0] + RADIUS , pos[1] + RADIUS))
                        checkerboard[placement_pos[0]][placement_pos[1]] = 1 # 흑돌 위치 표시
                        black = False
                        if winner(placement_pos, BLACKWINCHECK): # 흑돌의 오목 완성 확인
                            text = font.render("Black win!", True, TEXT_COLOR)
                            TEXT_WIDTH, TEXT_HEIGHT = text.get_size()
                            TEXT_X, TEXT_Y = (SCREEN_LENGTH - TEXT_WIDTH) / 2, (SCREEN_LENGTH - TEXT_HEIGHT) / 2
                            show_text = True
                            end = True

                    elif not black and stone_value == 0: # 백돌 착수
                        placement_poses.append((pos[0] + RADIUS , pos[1] + RADIUS))
                        checkerboard[placement_pos[0]][placement_pos[1]] = -1 # 백돌 위치 표시
                        black = True
                        if winner(placement_pos, WHITEWINCHECK): # 백돌의 오목 완성 확인
                            text = font.render("White win!", True, TEXT_COLOR)
                            TEXT_WIDTH, TEXT_HEIGHT = text.get_size()
                            TEXT_X, TEXT_Y = (SCREEN_LENGTH - TEXT_WIDTH) / 2, (SCREEN_LENGTH - TEXT_HEIGHT) / 2
                            show_text = True
                            end = True
                    #break
        
    mouse_pos = pygame.mouse.get_pos()
    
    # 예상 착수 지점
    if not end:
        for i in range(361):
            if rects[i].collidepoint(mouse_pos):
                stone_value = checkerboard[checkerboard_pos[i][0]][checkerboard_pos[i][1]]
                if black and stone_value == 0: # 흑돌의 예상 착수 지점
                    circle_rect = rects[i]
                    pygame.draw.circle(circle, (0, 0, 0, 128), (RADIUS, RADIUS), RADIUS)
                elif not black and stone_value == 0: # 백돌의 예상 착수 지점
                    circle_rect = rects[i]
                    pygame.draw.circle(circle, (255, 255, 255, 128), (RADIUS, RADIUS), RADIUS)
    
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
            pygame.draw.circle(screen, (0, 0, 0), placement_poses[i], RADIUS)
        else: # 백돌 착수
            pygame.draw.circle(screen, (255, 255, 255), placement_poses[i], RADIUS)
    
    if show_text:
        screen.blit(text, (TEXT_X, TEXT_Y))
    
    pygame.display.flip()

pygame.quit()