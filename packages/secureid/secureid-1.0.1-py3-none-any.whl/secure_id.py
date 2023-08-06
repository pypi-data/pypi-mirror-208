import random
from random import sample
__version__="1.0.1"
lettremin=["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
lettremaj=["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
chiffre=["0","1","2","3","4","5","6","7","8","9"]
def sid1():
    ensemble=lettremin+lettremaj+chiffre
    random.shuffle(ensemble)
    boucle=int(random.choice(chiffre))
    for i in range(boucle):
        random.shuffle(ensemble)
    code=random.randint(1000,9999)
    result=str(code)
    certif=""
    for i in range(8):
        if random.randint(0,1)==1:
            certif+=str(random.choice(lettremaj))
        else:
            certif+=str(random.choice(lettremin))
    certiflong=certif*code
    lettre=certiflong[code]
    result+="-"+certif
    result+="-"+lettre
    court=""
    for i in range(3):
        court=""
        for i in range(4):
            court+=str(random.choice(ensemble))
        result+="-"+court
    longstr=""
    for i in range(24):
        longstr+=str(random.choice(ensemble))
    result+="-"+longstr
    result+="-1"
    return(result)
def sid2():
    ensemble=lettremin+lettremaj+chiffre
    random.shuffle(ensemble)
    boucle=int(random.choice(chiffre))
    for i in range(boucle):
        random.shuffle(ensemble)
    code=random.randint(100000,999999)
    result=str(code)
    certif=""
    for i in range(12):
        if random.randint(0,1)==1:
            certif+=str(random.choice(lettremaj))
        else:
            certif+=str(random.choice(lettremin))
    certiflong=certif*code
    lettre=certiflong[code]
    result+="-"+certif
    result+="-"+lettre
    court=""
    for i in range(3):
        court=""
        for i in range(4):
            court+=str(random.choice(ensemble))
        result+="-"+court
    longstr=""
    for i in range(24):
        longstr+=str(random.choice(ensemble))
    result+="-"+longstr
    result+="-2"
    return(result)
if __name__=="__main__":
    print(sid2())