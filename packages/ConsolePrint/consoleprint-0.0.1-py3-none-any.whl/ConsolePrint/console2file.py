"""This module  saves terminal output to file."""
import sys

def startConsoleSave():
    """Starts the process to save the output to file"""
    global filename
    filename = input("Enter name of file or filepath: ") # specified filename/path      
    sys.stdout = open(filename, 'a')  # redirects output to specified file


def endConsoleSave():  
    """Ends the save to file process and returns output to console"""  
    sys.stdout.close()
    sys.stdout = sys.__stdout__   # redirects output from file back to terminal
    print(f"Output saved to {filename}")

if __name__ == "__main__":
    print("Running module test")
    import calendar
    
    startConsoleSave()
    
    print("Printing Calendar")
    print(calendar.calendar(2023))
    
    endConsoleSave()    
    
    # Alternatively using the with keyword
    with open("output.txt", 'a') as sys.stdout:
        print("hello using with to open and close")

    sys.stdout = sys.__stdout__