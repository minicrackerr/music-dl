MAX_SEARCH_RESULTS = 10
OUTPUT_FOLDER = "output"

def print_log(label,message):
    print(f">>> {label} || {message}")

def illegal_characters(string: str):
    for x in ["\\","/",":","*","?",'"',"<",">","|"]:
        string = string.replace(x,"")
    return string