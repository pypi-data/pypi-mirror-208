import random
__version__="1.3"
text="hello"
carac=["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","0","1","2","3","4","5","6","7","8","9","&","é","~",'"',"#","{","}","(",")","[","]","-","è","_","\\","ç","^","à","@","°","+","=","ê","ë","$","£","%","ù","µ","*",",","?",".",";",":","/","!","§"]
class CodeError(Exception):
    pass
class DecodeError(Exception):
    pass
class KeyElementError(Exception):
    pass
class KeyLengthError(Exception):
    pass
def generate_key():
    carac=["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","0","1","2","3","4","5","6","7","8","9","&","é","~",'"',"#","{","}","(",")","[","]","-","è","_","\\","ç","^","à","@","°","+","=","ê","ë","$","£","%","ù","µ","*",",","?",".",";",":","/","!","§"]
    random.shuffle(carac)
    key=""
    for i in range(len(carac)):
        key=key+carac[i]
    return key
def code(text,key):
    newtext=""
    incode={}
    if not type(text)==str:
        raise TypeError("text argument must be a string")
    if not type(key)==str:
        raise TypeError("key argument must be a string")
    keylist=list(key)
    if not len(keylist)==len(carac):
        raise KeyLengthError("the key is not of the expected length.")
    for i in range(len(keylist)):
        if not keylist[i] in carac:
            raise KeyElementError("'"+keylist[i]+"' must not be in the key.")
    for i in range(len(key)):
        incode.update({carac[i]:key[i]})
    incode.update({" ":" "})
    for i in range(len(text)):
        if not text[i] in carac:
            raise CodeError("'"+text[i]+"' is not encodable.")
        newtext=newtext+incode[text[i]]
    return newtext
def decode(text,key):
    newtext=""
    uncode={}
    if not type(text)==str:
        raise TypeError("text argument must be a string")
    if not type(key)==str:
        raise TypeError("key argument must be a string")
    keylist=list(key)
    if not len(keylist)==len(carac):
        raise KeyLengthError("the key is not of the expected length.")
    for i in range(len(keylist)):
        if not keylist[i] in carac:
            raise KeyElementError("'"+keylist[i]+"' must not be in the key.")
    for i in range(len(key)):
        uncode.update({key[i]:carac[i]})
    uncode.update({" ":" "})
    for i in range(len(text)):
        if not text[i] in carac:
            raise DecodeError("'"+text[i]+"' is not decodable.")
        newtext=newtext+uncode[text[i]]
    return newtext
if __name__=="__main__":
    keya=generate_key()
    print(keya)
    icode=code(text,keya)
    print(icode)
    decod=decode(icode,keya)
    print(decod)