import sys
sys.path.append('/home/ningweixi/projects/MISC/anutils/anutils/src')

from anutils import timing, print_with_time, silent, get_user_choice
from anutils.mlutils import get_learning_curve_from_txt
from anutils.scutils import read_10X_multi

@timing
def test_main():
    print('test start.')
    print('the next 2 sentences will be silenced.')
    @silent()
    def silent_print(string):
        print(string)
    silent_print('I will be silenced!')

    key = get_user_choice('choice test')
    print(f'received {key}.')

    print_with_time('test finished!')

test_main()