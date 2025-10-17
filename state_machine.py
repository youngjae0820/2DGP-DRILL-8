from event_to_string import event_to_string

class StateMachine:
    def __init__(self, start_state, rules):
        self.cur_state = start_state
        self.rules = rules
        self.cur_state.enter(('start', 0))

    def update(self):
        self.cur_state.do()

    def draw(self):
        self.cur_state.draw()

    def handle_state_event(self, state_event):
        #상태 변환 테이블을 만들어 내부로 가져오도록 한다. 상태 변환 테이블을 딕셔너리 데이터로 만든다. 딕셔너리를 만들떄 현재상태, 키를 넣으면 value값이 나오도록
        #두 객체 사이의 조건은 함수로 만든다.
        #keys()는 현제 딕셔너리에 있는 모든 함수
        for check_event in self.rules[self.cur_state].keys():   #self.rules[self.cur_state].keys() = 스페이스바
            if check_event(state_event): #만약 이것이 True면
                self.next_state = self.rules[self.cur_state][check_event]  # = IDLE
                self.cur_state.exit(state_event)
                self.next_state.enter(state_event)
                #현재 상태가 어떠 이벤트에 의해서 다음상태로 바뀌는지 정보를 표시
                print(f'{self.cur_state.__class__.__name__} -----------{event_to_string(state_event)}----------> {self.next_state.__class__.__name__}')
                self.cur_state = self.next_state
                return
        #처리되지 않은 이벤트를 출력
        print(f'처리되지 않은 이벤트{event_to_string(state_event)}가 있습니다.')



