import streamlit as st
import time

# Import cipher functions from your existing gui.py
from gui import (
    caesar_encrypt, caesar_decrypt,
    mono_encrypt, mono_decrypt,
    playfair_encrypt, playfair_decrypt,
    hill_encrypt, hill_decrypt,
    vigenere_encrypt, vigenere_decrypt,
    otp_process,
    rail_encrypt, rail_decrypt,
    columnar_encrypt, columnar_decrypt
)

st.set_page_config(
    page_title="Classical Cryptography Toolkit",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 Classical Cryptography Toolkit")
st.caption("Encryption • Decryption • Classical Ciphers")

ciphers = [
    "Caesar Cipher",
    "Monoalphabetic Cipher",
    "Playfair Cipher",
    "Hill Cipher",
    "Vigenere Cipher",
    "One-Time Pad",
    "Rail Fence Cipher",
    "Columnar Transposition"
]

cipher = st.sidebar.selectbox("Select Cipher", ciphers)

st.subheader(f"Selected Cipher: {cipher}")

text = st.text_area("Input Text")

# Dynamic key input
key = None

if cipher == "Caesar Cipher":
    key = st.number_input("Integer Shift Key", step=1)

elif cipher == "Monoalphabetic Cipher":
    key = st.text_input("26-letter Substitution Alphabet")

elif cipher == "Playfair Cipher":
    key = st.text_input("Keyword")

elif cipher == "Hill Cipher":
    st.write("Enter 2×2 Matrix")
    a = st.number_input("a", step=1)
    b = st.number_input("b", step=1)
    c = st.number_input("c", step=1)
    d = st.number_input("d", step=1)
    key = [[int(a), int(b)], [int(c), int(d)]]

elif cipher == "Vigenere Cipher":
    key = st.text_input("Alphabetic Keyword")

elif cipher == "One-Time Pad":
    key = st.text_input("OTP Key")

elif cipher == "Rail Fence Cipher":
    key = st.number_input("Number of Rails", min_value=2, step=1)

elif cipher == "Columnar Transposition":
    key = st.text_input("Keyword")

col1, col2 = st.columns(2)

if "result" not in st.session_state:
    st.session_state.result = ""

with col1:
    if st.button("🔒 Encrypt", use_container_width=True):

        try:
            start = time.perf_counter()

            if cipher == "Caesar Cipher":
                result = caesar_encrypt(text, int(key))

            elif cipher == "Monoalphabetic Cipher":
                result = mono_encrypt(text, key)

            elif cipher == "Playfair Cipher":
                result = playfair_encrypt(text, key)

            elif cipher == "Hill Cipher":
                result = hill_encrypt(text, key)

            elif cipher == "Vigenere Cipher":
                result = vigenere_encrypt(text, key)

            elif cipher == "One-Time Pad":
                result = otp_process(text, key, decrypt=False)

            elif cipher == "Rail Fence Cipher":
                result = rail_encrypt(text, int(key))

            elif cipher == "Columnar Transposition":
                result = columnar_encrypt(text, key)

            elapsed = time.perf_counter() - start

            st.session_state.result = result

            st.success("Encryption successful")
            st.caption(f"Time: {elapsed:.8f} seconds")

        except Exception as e:
            st.error(str(e))

with col2:
    if st.button("🔓 Decrypt", use_container_width=True):

        try:
            start = time.perf_counter()

            ciphertext = st.session_state.result or text

            if cipher == "Caesar Cipher":
                result = caesar_decrypt(ciphertext, int(key))

            elif cipher == "Monoalphabetic Cipher":
                result = mono_decrypt(ciphertext, key)

            elif cipher == "Playfair Cipher":
                result = playfair_decrypt(ciphertext, key)

            elif cipher == "Hill Cipher":
                result = hill_decrypt(ciphertext, key)

            elif cipher == "Vigenere Cipher":
                result = vigenere_decrypt(ciphertext, key)

            elif cipher == "One-Time Pad":
                result = otp_process(ciphertext, key, decrypt=True)

            elif cipher == "Rail Fence Cipher":
                result = rail_decrypt(ciphertext, int(key))

            elif cipher == "Columnar Transposition":
                result = columnar_decrypt(ciphertext, key)

            elapsed = time.perf_counter() - start

            st.session_state.result = result

            st.success("Decryption successful")
            st.caption(f"Time: {elapsed:.8f} seconds")

        except Exception as e:
            st.error(str(e))

st.subheader("Result")

st.code(st.session_state.result)

# =========================================================
# VISUALIZATION
# =========================================================

st.subheader("📊 Visualization")

if cipher == "Caesar Cipher":

    shift = int(key) % 26

    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    shifted = alphabet[shift:] + alphabet[:shift]

    st.write("### Caesar Shift Mapping")

    st.code(
        "Plain : " + alphabet + "\n"
        "Cipher : " + shifted
    )

    st.info(f"Each letter is shifted by {shift} position(s).")


elif cipher == "Monoalphabetic Cipher":

    if key and len(key) == 26:

        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        st.write("### Substitution Mapping")

        mapping = ""

        for p, c in zip(alphabet, key.upper()):
            mapping += f"{p} → {c}    "

        st.code(mapping)

        st.write("**Plain Alphabet**")
        st.code(alphabet)

        st.write("**Cipher Alphabet**")
        st.code(key.upper())

    else:
        st.info("Enter a valid 26-letter substitution alphabet.")


elif cipher == "Playfair Cipher":

    if key:

        keyword = "".join(
            ch for ch in key.upper()
            if ch.isalpha()
        )

        alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"

        sequence = ""

        for ch in keyword + alphabet:
            if ch not in sequence:
                sequence += ch

        matrix = [
            sequence[i:i+5]
            for i in range(0, 25, 5)
        ]

        st.write("### Playfair 5 × 5 Matrix")

        for row in matrix:
            st.code("   ".join(row))

    else:
        st.info("Enter a Playfair keyword.")


elif cipher == "Hill Cipher":

    st.write("### Hill Cipher Matrix")

    matrix_text = (
        f"[ {int(a):2d}  {int(b):2d} ]\n"
        f"[ {int(c):2d}  {int(d):2d} ]"
    )

    st.code(matrix_text)

    determinant = int(a) * int(d) - int(b) * int(c)

    st.write(f"**Determinant:** {determinant}")

    if determinant % 26 == 0:
        st.warning(
            "This matrix is not invertible modulo 26. "
            "Choose another matrix for decryption."
        )
    else:
        st.success("Matrix can potentially be used modulo 26.")


elif cipher == "Vigenere Cipher":

    if key:

        clean_key = "".join(
            ch for ch in key.upper()
            if ch.isalpha()
        )

        clean_text = "".join(
            ch for ch in text.upper()
            if ch.isalpha()
        )

        if clean_key:

            repeated_key = (
                clean_key *
                ((len(clean_text) // len(clean_key)) + 1)
            )[:len(clean_text)]

            st.write("### Vigenère Key Alignment")

            st.code(
                "Text : " + clean_text + "\n"
                "Key  : " + repeated_key
            )

            st.info(
                f"Keyword: {clean_key}"
            )

    else:
        st.info("Enter an alphabetic keyword.")


elif cipher == "One-Time Pad":

    st.write("### One-Time Pad")

    if key:

        st.code(
            "Input : " + text.upper() + "\n"
            "Key   : " + key.upper()
        )

        st.info(
            "The OTP key should be the same length as the "
            "alphabetic characters in the input."
        )

    else:
        st.info("Enter an OTP key.")


elif cipher == "Rail Fence Cipher":

    rails = int(key)

    st.write("### Rail Fence Zig-Zag Pattern")

    clean_text = text

    if clean_text:

        pattern = []

        rail = 0
        direction = 1

        for char in clean_text:

            pattern.append((rail, char))

            if rail == 0:
                direction = 1

            elif rail == rails - 1:
                direction = -1

            rail += direction

        for r in range(rails):

            line = ""

            for rr, char in pattern:

                if rr == r:
                    line += char
                else:
                    line += " "

            st.code(f"Rail {r + 1}: {line}")

    st.info(f"Number of rails: {rails}")


elif cipher == "Columnar Transposition":

    if key:

        clean_key = "".join(
            ch for ch in key.upper()
            if ch.isalpha()
        )

        st.write("### Columnar Transposition")

        st.write("**Keyword:**")

        st.code(clean_key)

        if clean_key:

            order = sorted(
                range(len(clean_key)),
                key=lambda i: (clean_key[i], i)
            )

            numbering = [""] * len(clean_key)

            for number, index in enumerate(order, start=1):
                numbering[index] = str(number)

            st.write("**Column Order:**")

            st.code(
                "Key   : " + "   ".join(clean_key) + "\n"
                "Order : " + "   ".join(numbering)
            )

    else:
        st.info("Enter a Columnar Transposition keyword.")