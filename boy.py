from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDLK_a

from state_machine import StateMachine

#이벤트 체크 함수

def right_down(e): #e가 오른쪽 key input인가를 확인
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT
def left_down(e): #e가 왼쪽 key input인가를 확인
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT
def right_up(e): #e가 오른쪽 key input인가를 확인
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT
def left_up(e): #e가 왼쪽 key input인가를 확인
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT
def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a

def time_out(e): #e가 시간초과 이벤트인가를 확인
    return e[0] == 'TIME_OUT'

def space_down(e): #e가 space key input인가를 확인
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE #핵심적인 부분!

class Run:

    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        if right_down(e) or left_up(e):
            self.boy.dir = self.boy.face_dir =1 #오른쪽
        elif left_down(e) or right_up(e):
            self.boy.dir = self.boy.face_dir =-1 #왼쪽

    def exit(self,e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8
        #2초가 경과하면 TIME_OUT 이벤트 발생
        self.boy.x += self.boy.dir *5

    def draw(self):
        if self.boy.face_dir == 1: # right
            self.boy.image.clip_draw(self.boy.frame * 100, 100, 100, 100, self.boy.x, self.boy.y)
        else: # face_dir == -1: # left
            self.boy.image.clip_draw(self.boy.frame * 100,   0, 100, 100, self.boy.x, self.boy.y)

class Sleep:

    def __init__(self, boy):
        self.boy = boy

    def enter(self,e):
        self.boy.dir = 0

    def exit(self,e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8

    def draw(self):
        if self.boy.face_dir == 1: # right
            self.boy.image.clip_composite_draw(self.boy.frame * 100, 300, 100, 100, 3.141592/2, '',self.boy.x -25, self.boy.y-25, 100, 100)
        else: # face_dir == -1: # left
            self.boy.image.clip_composite_draw(self.boy.frame * 100, 200, 100, 100, -3.141592/2, '', self.boy.x-25, self.boy.y-25, 100, 100)

class Idle:

    def __init__(self, boy):
        self.boy = boy

    def enter(self,e):
        self.boy.dir = 0
        self.boy.wait_start_time = get_time() #변경 시작 시간을 기록

    def exit(self,e):
        pass


    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8
        #2초가 경과하면 TIME_OUT 이벤트 발생
        if get_time() - self.boy.wait_start_time > 2.0:
            self.boy.state_machine.handle_state_event(('TIME_OUT', 0))

    def draw(self):
        if self.boy.face_dir == 1: # right
            self.boy.image.clip_draw(self.boy.frame * 100, 300, 100, 100, self.boy.x, self.boy.y)
        else: # face_dir == -1: # left
            self.boy.image.clip_draw(self.boy.frame * 100, 200, 100, 100, self.boy.x, self.boy.y)

class AutoRun:
    def __init__(self, boy):
        self.boy = boy
        self.speed = 12
        self.scale = 140

    def enter(self, e):
        self.boy.dir = -1
        self.boy.face_dir = -1
        self.start_time = get_time()

    def exit(self, e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8
        self.boy.x += self.boy.dir * self.speed
        # 좌 우끝에서 방향전환
        if self.boy.x < 50:
            self.boy.x = 50
            self.boy.dir = self.boy.face_dir = 1
        elif self.boy.x > 750:
            self.boy.x = 750
            self.boy.dir = self.boy.face_dir = -1
            # 5초 경과 시 TIME_OUT 발생
        if get_time() - self.start_time > 5.0:
            self.boy.state_machine.handle_state_event(('TIME_OUT', None))

    def draw(self):
        row = 100 if self.boy.face_dir == 1 else 0
        self.boy.image.clip_composite_draw(
            self.boy.frame * 100, row, 100, 100, 0, '', self.boy.x, self.boy.y, self.scale, self.scale
        )

class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.image = load_image('animation_sheet.png')

        self.IDLE = Idle(self)
        self.SLEEP = Sleep(self)
        self.RUN = Run(self)
        self.AUTORUN = AutoRun(self)

        self.state_machine = StateMachine(
            self.IDLE, #초기상태
            {
                self.SLEEP : {space_down: self.IDLE},
                self.IDLE : {left_up: self.RUN, right_up: self.RUN, left_down: self.RUN, right_down: self.RUN, time_out : self.SLEEP, a_down: self.AUTORUN},
                self.RUN : {right_down: self.IDLE, left_up: self.IDLE,left_down: self.IDLE, right_up: self.IDLE},
                self.AUTORUN: {time_out: self.IDLE, right_down: self.RUN, left_down: self.RUN}
            }
        )

    def update(self):
        self.state_machine.update()


    def draw(self):
        self.state_machine.draw()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
        pass
