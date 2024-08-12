def import_words():
    with open('./r_word.txt', "r" ) as file:
        for line in file:
            print(line, end='')
import_words()