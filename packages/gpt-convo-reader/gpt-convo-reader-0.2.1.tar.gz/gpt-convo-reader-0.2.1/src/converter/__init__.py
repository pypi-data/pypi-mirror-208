import sys
from converter import gui


def start(): # pragma: no cover
    if len(sys.argv) != 1:
        print('usage: python3 gpt_reader_gui')
        sys.exit(1)
    app = gui.ConversationGUI()
    app.font = "Helvetica"
    app.text_size = 12
    # Show the app
    app.display()


if __name__ == '__main__': # pragma: no cover
    start()