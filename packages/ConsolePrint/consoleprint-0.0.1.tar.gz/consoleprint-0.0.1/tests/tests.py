countdown(10)
loading1(20)  
loading2(10, 'thinking...')
loading3(10)


printing("This text prints word by word. Cool isn't it?", style='word', delay=0.3)
printing("This text prints letter by letter and does not move to the new line", 0.06, 'letter', False, False)
print()
printing("This text prints letter by letter but in reverse", rev=True)
flashprint("This entire Text is flashing")
flashtext('The word at the end of this text is ', 'flashing', delay=0.2, blinks=5)
animate1("This text is animated with # symbol")
animate2("This text is animated with # symbol")