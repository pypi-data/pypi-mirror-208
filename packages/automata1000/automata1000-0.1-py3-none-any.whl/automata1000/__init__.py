def info():
    print("""
from automata.fa.dfa import DFA
dfa=DFA(
    sates={'q0','q1','q2','q3'},
    input_symbols={'0','1'},
    transistions={
        'q0':{'0':'q2','1':'q1'},
        'q0':{'0':'q2','1':'q1'},
        'q0':{'0':'q2','1':'q1'},
        'q0':{'0':'q2','1':'q1'},
    },
    intial_state='q0',
    final_states={'q2'}
)
dfa.read_input('11111100')
if dfa.accepts_input('11111100'):
  print('accepted')
else:
  print('rejected')
    """)