

def load_word_list(filename):
    with open(filename, 'r',encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]
    
def save_word_list(filename, word_list,mode = 'w'):
    with open(filename, mode ,encoding="utf-8") as f:
        for word in word_list:
            f.write(f"{word.strip().lower()}\n")

