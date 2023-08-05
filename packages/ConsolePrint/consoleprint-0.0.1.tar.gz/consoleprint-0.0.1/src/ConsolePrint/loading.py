import time

def countdown(t):
    '''Enter countdown time in seconds'''
    # t = int(input('Enter time in secs: '))
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")        
        time.sleep(1)
        t -= 1
    if __name__ == '__main__':
        print('Timer completed!')

def loading1(t):
    x = t
    percent = 0
    for _ in range(t):        
        percent += 100 / x
        y = round(percent, 1) / 100
        print(f" Loading... [{'|||' * _}{'   ' * (x - _ - 1)}]", '{:4.0%}'.format(y), end="\r")
        time.sleep(0.2)
        t -= 1
    time.sleep(0.5)
    if __name__ == '__main__':
        print('\nLoading Complete!')

def loading2(t, text='Loading...'):
    "Takes two arguments, time and text to display such as 'loading...'"
    load = ['-', '\\', '|', '/', ] * t
    for _ in load:
        print(f"  {_}  {text}", end='\r')
        time.sleep(0.5)
    if __name__ == '__main__':
        print('\nLoading Complete!')
    
def loading3(t):
    the_bar = "     ======     "
    nums = ([*range(len(the_bar)-5)] + [*range(len(the_bar) - 7, 0, -1)]) * t
    for a in nums:
        print(f' [{the_bar[a:a + 6]}]', end='\r')
        time.sleep(0.2) 
    if __name__ == '__main__':
        print('\nLoading Complete!')


if __name__ == '__main__':
    countdown(5)
    loading1(20)  
    loading2(10, 'thinking...')
    loading3(10)
  

   