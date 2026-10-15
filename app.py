import streamlit as st
import time
import string
import math

ALPHABET = string.ascii_uppercase

def caesar_encrypt(text, shift):
    out = ""
    for ch in text:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            out += chr((ord(ch) - base + shift) % 26 + base)
        else:
            out += ch
    return out

def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)

def mono_key(key):
    key = key.upper().replace(" ", "")
    if len(key) != 26 or not key.isalpha() or len(set(key)) != 26:
        raise ValueError("Monoalphabetic key must contain exactly 26 unique letters.")
    return key

def mono_encrypt(text, key):
    key = mono_key(key)
    return "".join(
        key[ord(ch.upper())-65] if ch.isalpha() else ch
        for ch in text
    )

def mono_decrypt(text, key):
    key = mono_key(key)
    inv = {key[i]: ALPHABET[i] for i in range(26)}
    return "".join(
        inv[ch.upper()] if ch.isalpha() else ch
        for ch in text
    )

def playfair_matrix(keyword):
    keyword = "".join(c for c in keyword.upper() if c.isalpha()).replace("J", "I")
    if not keyword:
        raise ValueError("Enter a Playfair keyword.")
    s = ""
    for c in keyword + "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if c not in s:
            s += c
    return [s[i:i+5] for i in range(0, 25, 5)]

def playfair_prepare(text):
    text = "".join(c for c in text.upper() if c.isalpha()).replace("J", "I")
    pairs, i = [], 0
    while i < len(text):
        a = text[i]
        if i + 1 >= len(text):
            pairs.append(a + "X"); i += 1
        elif a == text[i+1]:
            pairs.append(a + "X"); i += 1
        else:
            pairs.append(a + text[i+1]); i += 2
    return pairs

def playfair_encrypt(text, keyword):
    m = playfair_matrix(keyword)
    pos = {m[r][c]:(r,c) for r in range(5) for c in range(5)}
    result = ""
    for a,b in playfair_prepare(text):
        ra,ca = pos[a]; rb,cb = pos[b]
        if ra == rb:
            result += m[ra][(ca+1)%5] + m[rb][(cb+1)%5]
        elif ca == cb:
            result += m[(ra+1)%5][ca] + m[(rb+1)%5][cb]
        else:
            result += m[ra][cb] + m[rb][ca]
    return result

def playfair_decrypt(text, keyword):
    m = playfair_matrix(keyword)
    pos = {m[r][c]:(r,c) for r in range(5) for c in range(5)}
    text = "".join(c for c in text.upper() if c.isalpha()).replace("J","I")
    if len(text) % 2:
        raise ValueError("Playfair ciphertext must contain an even number of letters.")
    result = ""
    for i in range(0,len(text),2):
        a,b = text[i],text[i+1]
        ra,ca = pos[a]; rb,cb = pos[b]
        if ra == rb:
            result += m[ra][(ca-1)%5] + m[rb][(cb-1)%5]
        elif ca == cb:
            result += m[(ra-1)%5][ca] + m[(rb-1)%5][cb]
        else:
            result += m[ra][cb] + m[rb][ca]
    return result

def mod_inverse(a, m=26):
    for x in range(1,m):
        if (a*x) % m == 1:
            return x
    raise ValueError("Matrix determinant has no modular inverse modulo 26.")

def validate_hill(matrix):
    a,b = matrix[0]; c,d = matrix[1]
    det = (a*d-b*c) % 26
    if math.gcd(det,26) != 1:
        raise ValueError("Hill matrix is not invertible modulo 26. Try [[3,3],[2,5]].")

def hill_encrypt(text, matrix):
    validate_hill(matrix)
    clean = "".join(c for c in text.upper() if c.isalpha())
    if len(clean) % 2: clean += "X"
    result = ""
    for i in range(0,len(clean),2):
        x,y = ord(clean[i])-65, ord(clean[i+1])-65
        result += chr((matrix[0][0]*x+matrix[0][1]*y)%26+65)
        result += chr((matrix[1][0]*x+matrix[1][1]*y)%26+65)
    return result

def hill_decrypt(text, matrix):
    validate_hill(matrix)
    clean = "".join(c for c in text.upper() if c.isalpha())
    if len(clean)%2: raise ValueError("Hill ciphertext must have even length.")
    a,b = matrix[0]; c,d = matrix[1]
    det = (a*d-b*c)%26
    inv = mod_inverse(det)
    im = [[d*inv%26, -b*inv%26],[-c*inv%26,a*inv%26]]
    return hill_encrypt(clean, im)

def vig_key(key):
    key = "".join(c for c in key.upper() if c.isalpha())
    if not key: raise ValueError("Vigenère key must contain letters.")
    return key

def vigenere(text,key,decrypt=False):
    key = vig_key(key); result=""; i=0
    for ch in text:
        if ch.isalpha():
            shift=ord(key[i%len(key)])-65
            if decrypt: shift=-shift
            base=ord("A") if ch.isupper() else ord("a")
            result += chr((ord(ch)-base+shift)%26+base); i+=1
        else: result += ch
    return result

def otp(text,key,decrypt=False):
    key="".join(c for c in key.upper() if c.isalpha())
    n=sum(c.isalpha() for c in text)
    if len(key)!=n: raise ValueError(f"OTP key must contain exactly {n} letters.")
    result=""; i=0
    for ch in text:
        if ch.isalpha():
            shift=ord(key[i])-65
            if decrypt: shift=-shift
            base=ord("A") if ch.isupper() else ord("a")
            result += chr((ord(ch)-base+shift)%26+base); i+=1
        else: result += ch
    return result

def rail_encrypt(text, rails):
    if rails<2: raise ValueError("Rails must be at least 2.")
    fence=[""]*rails; r=0; d=1
    for ch in text:
        fence[r]+=ch
        if r==0: d=1
        elif r==rails-1: d=-1
        r+=d
    return "".join(fence)

def rail_decrypt(text, rails):
    if rails<2: raise ValueError("Rails must be at least 2.")
    pattern=[]; r=0; d=1
    for _ in text:
        pattern.append(r)
        if r==0: d=1
        elif r==rails-1: d=-1
        r+=d
    counts=[pattern.count(i) for i in range(rails)]
    fence=[]; p=0
    for n in counts:
        fence.append(list(text[p:p+n])); p+=n
    idx=[0]*rails; out=""
    for r in pattern:
        out+=fence[r][idx[r]]; idx[r]+=1
    return out

def col_order(key):
    key="".join(c for c in key.upper() if c.isalpha())
    if not key: raise ValueError("Enter a Columnar keyword.")
    return key, sorted(range(len(key)), key=lambda i:(key[i],i))

def columnar_encrypt(text,key):
    key,order=col_order(key)
    clean="".join(c for c in text.upper() if c.isalpha())
    rows=(len(clean)+len(key)-1)//len(key)
    padded=clean.ljust(rows*len(key),"X")
    grid=[padded[i:i+len(key)] for i in range(0,len(padded),len(key))]
    return "".join(grid[r][c] for c in order for r in range(rows))

def columnar_decrypt(text,key):
    key,order=col_order(key)
    clean="".join(c for c in text.upper() if c.isalpha())
    if len(clean)%len(key): raise ValueError("Invalid ciphertext length.")
    rows=len(clean)//len(key); grid=[[""]*len(key) for _ in range(rows)]
    p=0
    for c in order:
        for r in range(rows):
            grid[r][c]=clean[p]; p+=1
    return "".join("".join(row) for row in grid).rstrip("X")

# ---------------- UI ----------------
st.set_page_config(page_title="Classical Cryptography Toolkit", page_icon="🔐", layout="wide")
st.title("🔐 CLASSICAL CRYPTOGRAPHY TOOLKIT")
st.caption("Encryption • Decryption • Classical Ciphers")

ciphers=["Caesar Cipher","Monoalphabetic Cipher","Playfair Cipher","Hill Cipher",
         "Vigenère Cipher","One-Time Pad","Rail Fence Cipher","Columnar Transposition"]
cipher=st.sidebar.selectbox("Select Cipher",ciphers)
st.subheader(f"Selected Cipher: {cipher}")
text=st.text_area("Input Text",height=140)
key=None

if cipher=="Caesar Cipher":
    key=st.number_input("Integer Shift Key",value=4,step=1)
elif cipher=="Monoalphabetic Cipher":
    key=st.text_input("26-letter Substitution Alphabet",placeholder="QWERTYUIOPASDFGHJKLZXCVBNM")
elif cipher=="Playfair Cipher":
    key=st.text_input("Keyword",placeholder="MONARCHY")
elif cipher=="Hill Cipher":
    st.write("2 × 2 Matrix")
    c1,c2=st.columns(2)
    with c1:
        a=st.number_input("a",value=3,step=1); c=st.number_input("c",value=2,step=1)
    with c2:
        b=st.number_input("b",value=3,step=1); d=st.number_input("d",value=5,step=1)
    key=[[int(a),int(b)],[int(c),int(d)]]
elif cipher=="Vigenère Cipher":
    key=st.text_input("Alphabetic Keyword",placeholder="SECURITY")
elif cipher=="One-Time Pad":
    key=st.text_input("OTP Key",placeholder="Same number of letters as input")
elif cipher=="Rail Fence Cipher":
    key=st.number_input("Number of Rails",min_value=2,value=3,step=1)
else:
    key=st.text_input("Keyword",placeholder="SECURITY")

if "result" not in st.session_state: st.session_state.result=""

def run_cipher(decrypt=False):
    start=time.perf_counter()
    source=st.session_state.result if decrypt and st.session_state.result else text
    if cipher=="Caesar Cipher": result=caesar_decrypt(source,int(key)) if decrypt else caesar_encrypt(source,int(key))
    elif cipher=="Monoalphabetic Cipher": result=mono_decrypt(source,key) if decrypt else mono_encrypt(source,key)
    elif cipher=="Playfair Cipher": result=playfair_decrypt(source,key) if decrypt else playfair_encrypt(source,key)
    elif cipher=="Hill Cipher": result=hill_decrypt(source,key) if decrypt else hill_encrypt(source,key)
    elif cipher=="Vigenère Cipher": result=vigenere(source,key,True) if decrypt else vigenere(source,key)
    elif cipher=="One-Time Pad": result=otp(source,key,True) if decrypt else otp(source,key)
    elif cipher=="Rail Fence Cipher": result=rail_decrypt(source,int(key)) if decrypt else rail_encrypt(source,int(key))
    else: result=columnar_decrypt(source,key) if decrypt else columnar_encrypt(source,key)
    st.session_state.result=result
    return time.perf_counter()-start

c1,c2=st.columns(2)
with c1:
    if st.button("🔒 Encrypt",use_container_width=True):
        try: st.success("Encryption successful"); st.caption(f"Execution time: {run_cipher():.8f} seconds")
        except Exception as e: st.error(str(e))
with c2:
    if st.button("🔓 Decrypt",use_container_width=True):
        try: st.success("Decryption successful"); st.caption(f"Execution time: {run_cipher(True):.8f} seconds")
        except Exception as e: st.error(str(e))

st.subheader("Result")
st.code(st.session_state.result if st.session_state.result else "No result yet.")

st.subheader("📊 Visualization")

if cipher=="Caesar Cipher":
    s=int(key)%26; shifted=ALPHABET[s:]+ALPHABET[:s]
    st.code("Plain  : "+ALPHABET+"\nCipher : "+shifted)
elif cipher=="Monoalphabetic Cipher":
    try:
        k=mono_key(key); st.code("Plain  : "+ALPHABET+"\nCipher : "+k)
    except: st.info("Enter a valid 26-letter substitution alphabet.")
elif cipher=="Playfair Cipher":
    try:
        for row in playfair_matrix(key): st.code("  ".join(row))
    except: st.info("Enter a Playfair keyword.")
elif cipher=="Hill Cipher":
    st.code(f"[ {a:2d}  {b:2d} ]\n[ {c:2d}  {d:2d} ]")
    det=a*d-b*c
    st.write(f"Determinant: {det} | mod 26: {det%26}")
    st.success("Matrix is invertible modulo 26.") if math.gcd(det%26,26)==1 else st.warning("Matrix is not invertible modulo 26.")
elif cipher=="Vigenère Cipher":
    try:
        k=vig_key(key); clean="".join(x for x in text.upper() if x.isalpha())
        if clean:
            rep=(k*((len(clean)//len(k))+1))[:len(clean)]
            st.code("Text : "+clean+"\nKey  : "+rep)
    except: st.info("Enter an alphabetic keyword.")
elif cipher=="One-Time Pad":
    k="".join(x for x in str(key).upper() if x.isalpha())
    st.code("Input : "+text.upper()+"\nKey   : "+k)
    st.info(f"Required key length: {sum(x.isalpha() for x in text)}")
elif cipher=="Rail Fence Cipher":
    rails=int(key); pattern=[]; r=0; d=1
    for ch in text:
        pattern.append((r,ch))
        if r==0: d=run
        elif r==rails-1: d=-1
        r+=d
    for rr in range(rails):
        st.code(f"Rail {rr+1}: "+"".join(ch if r==rr else " " for r,ch in pattern))
elif cipher=="Columnar Transposition":
    try:
        k,order=col_order(key); nums=[""]*len(k)
        for n,i in enumerate(order,1): nums[i]=str(n)
        st.code("Key   : "+"   ".join(k)+"\nOrder : "+"   ".join(nums))
    except: st.info("Enter a keyword.")

st.divider()
st.caption("Classical Cryptography Toolkit • Python + Streamlit")
