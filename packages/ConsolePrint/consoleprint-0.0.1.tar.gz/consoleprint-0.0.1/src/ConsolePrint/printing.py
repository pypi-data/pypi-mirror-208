import time
import os

if __name__ == "__main__":
    os.system('cls')


def printing(text, delay=0.05, style='letter', new_line=True, rev=False):
    """Prints text to console letter by letter or word by word"""
    match rev:
        case False:
            if style.lower() == 'letter':
                for _ in range(len(text)):
                    print(text[:_ + 1], end='\r')
                    time.sleep(delay)
            elif style.lower() == 'word':
                text = text.split(' ')
                for _ in range(len(text)):
                    print(' '.join(text[:_ + 1]), end='\r')
                    time.sleep(delay)
        case True:
            if style.lower() == 'letter':
                for _ in range(len(text)):
                    print(text[-1 - _:], end='\r')
                    time.sleep(delay)
            elif style.lower() == 'word':
                text = text.split(' ')
                for _ in range(len(text)):
                    print(' '.join(text[-1 - _:]), end='\r')
                    time.sleep(delay)
    if new_line:
        print()


def flashprint(text, flashes=5, delay=0.2, stay=True):
    """Gets printed output to blink"""
    for _ in range(flashes):
        print(text, end='\r'), time.sleep(delay)
        print(' ' * len(text), end='\r'), time.sleep(delay)
    if stay:
        print(text)


def flashtext(phrase, text, blinks=5, index='end', delay=0.2):
    """Hilights key word by flashing"""
    textb = ' ' * len(text)
    if index == 'end':
        phrase1 = phrase
        phrase2 = ''
    else:
        phrase1 = phrase[:index]
        phrase2 = phrase[index:]

    for _ in range(blinks):
        print(phrase1 + text + phrase2, end='\r')
        time.sleep(delay)
        print(phrase1 + textb + phrase2, end='\r')
        time.sleep(delay)
    print(phrase1 + text + phrase2)


def animate1(text, symbol="#"):
    """Flashing masked text to transition to flasing text"""
    symbol = len(text) * symbol
    flashprint(symbol, flashes=3, stay=False)
    flashprint(text, flashes=2, stay=True)


def animate2(text, symbol="#", delay=0.05):
    """Reveals all characters text by text but first masked then flashes"""
    symbol = len(text) * symbol
    for _ in symbol + "\r" + text + "\r":
        print(_, end="", flush=True)
        time.sleep(delay)
    flashprint(text, flashes=2, stay=True)


# Code test
if __name__ == "__main__":
    printing("This text prints word by word. Cool isn't it?", style='word', delay=0.3)
    printing("This text prints letter by letter and does not move to the new line", 0.06, 'letter', False, False)
    print()
    printing("This text prints letter by letter but in reverse", rev=True)
    flashprint("This entire Text is flashing")
    flashtext('The word at the end of this text is ', 'flashing', delay=0.2, blinks=5)
    animate1("This text is animated with # symbol")
    animate2("This text is animated with # symbol")
