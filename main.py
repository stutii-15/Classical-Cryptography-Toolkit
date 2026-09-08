
import string
import time
import random
from pathlib import Path

ALPHABET = string.ascii_uppercase


# ============================================================
# BASIC HELPERS
# ============================================================

def clean_letters(text):
    """Return only A-Z letters in uppercase."""
    return "".join(ch for ch in text.upper() if ch in ALPHABET)


def preserve_case_replace(text, transform_func):
    """Transform only letters and preserve spaces/punctuation/case."""
    letters = [ch for ch in text if ch.upper() in ALPHABET]
    transformed = transform_func("".join(ch.upper() for ch in letters))

    result = []
    i = 0

    for ch in text:
        if ch.upper() in ALPHABET:
            out = transformed[i]
            result.append(out if ch.isupper() else out.lower())
            i += 1
        else:
            result.append(ch)

    return "".join(result)


def mod_inverse(a, m=26):
    a %= m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None


# ============================================================
# 1. CAESAR CIPHER
# ============================================================

def caesar_encrypt(text, key):
    key %= 26

    def transform(s):
        return "".join(
            chr((ord(ch) - 65 + key) % 26 + 65)
            for ch in s
        )

    return preserve_case_replace(text, transform)


def caesar_decrypt(text, key):
    return caesar_encrypt(text, -key)


# ============================================================
# 2. MONOALPHABETIC CIPHER
# ============================================================

def validate_substitution_key(key):
    key = key.upper().replace(" ", "")

    if len(key) != 26:
        raise ValueError(
            "Substitution key must contain exactly 26 letters."
        )

    if not all(ch in ALPHABET for ch in key):
        raise ValueError(
            "Substitution key must contain only A-Z letters."
        )

    if len(set(key)) != 26:
        raise ValueError(
            "Substitution key must contain 26 unique letters."
        )

    return key


def monoalphabetic_encrypt(text, key):
    key = validate_substitution_key(key)

    table = str.maketrans(
        ALPHABET + ALPHABET.lower(),
        key + key.lower()
    )

    return text.translate(table)


def monoalphabetic_decrypt(text, key):
    key = validate_substitution_key(key)

    reverse = str.maketrans(
        key + key.lower(),
        ALPHABET + ALPHABET.lower()
    )

    return text.translate(reverse)


# ============================================================
# 3. PLAYFAIR CIPHER
# ============================================================

def playfair_square(key):
    key = clean_letters(key).replace("J", "I")

    sequence = []

    for ch in key + ALPHABET:
        ch = "I" if ch == "J" else ch

        if ch not in sequence:
            sequence.append(ch)

    square = [
        sequence[i:i + 5]
        for i in range(0, 25, 5)
    ]

    positions = {}

    for r in range(5):
        for c in range(5):
            positions[square[r][c]] = (r, c)

    positions["J"] = positions["I"]

    return square, positions


def display_playfair_square(key):
    square, _ = playfair_square(key)

    print("\nPlayfair 5 x 5 Key Matrix:")
    print("--------------------------")

    for row in square:
        print("  ".join(row))

    print("--------------------------")


def playfair_prepare_plaintext(text):
    s = clean_letters(text).replace("J", "I")

    pairs = []
    i = 0

    while i < len(s):

        a = s[i]

        if i + 1 >= len(s):
            pairs.append(a + "X")
            i += 1

        else:
            b = s[i + 1]

            if a == b:
                pairs.append(a + "X")
                i += 1

            else:
                pairs.append(a + b)
                i += 2

    return pairs


def playfair_transform_pair(
    a, b, square, positions, encrypt=True
):
    ra, ca = positions[a]
    rb, cb = positions[b]

    step = 1 if encrypt else -1

    # Same row
    if ra == rb:
        return (
            square[ra][(ca + step) % 5],
            square[rb][(cb + step) % 5]
        )

    # Same column
    elif ca == cb:
        return (
            square[(ra + step) % 5][ca],
            square[(rb + step) % 5][cb]
        )

    # Rectangle rule
    else:
        return (
            square[ra][cb],
            square[rb][ca]
        )


def playfair_encrypt(text, key):
    square, positions = playfair_square(key)

    pairs = playfair_prepare_plaintext(text)

    result = []

    for pair in pairs:
        a, b = playfair_transform_pair(
            pair[0],
            pair[1],
            square,
            positions,
            True
        )

        result.extend([a, b])

    return "".join(result)


def playfair_decrypt(text, key):
    square, positions = playfair_square(key)

    s = clean_letters(text).replace("J", "I")

    if len(s) % 2 != 0:
        s += "X"

    result = []

    for i in range(0, len(s), 2):

        a, b = playfair_transform_pair(
            s[i],
            s[i + 1],
            square,
            positions,
            False
        )

        result.extend([a, b])

    return "".join(result)


# ============================================================
# 4. HILL CIPHER - 2 x 2
# ============================================================

def parse_hill_key(key):

    parts = key.replace(",", " ").split()

    if len(parts) != 4:
        raise ValueError(
            "Hill key must contain 4 numbers. Example: 3 3 2 5"
        )

    try:
        values = [int(x) % 26 for x in parts]
    except ValueError:
        raise ValueError(
            "Hill key must contain numbers only."
        )

    return [
        [values[0], values[1]],
        [values[2], values[3]]
    ]


def display_hill_matrix(key):

    matrix = parse_hill_key(key)

    print("\nHill Cipher Key Matrix:")
    print("-----------------------")
    print(f"| {matrix[0][0]:2} {matrix[0][1]:2} |")
    print(f"| {matrix[1][0]:2} {matrix[1][1]:2} |")
    print("-----------------------")


def hill_inverse_matrix(matrix):

    a, b = matrix[0]
    c, d = matrix[1]

    determinant = (a * d - b * c) % 26

    inv_det = mod_inverse(determinant, 26)

    if inv_det is None:
        raise ValueError(
            "Hill key cannot be inverted modulo 26. "
            "Use the example key: 3 3 2 5"
        )

    return [
        [
            (d * inv_det) % 26,
            (-b * inv_det) % 26
        ],
        [
            (-c * inv_det) % 26,
            (a * inv_det) % 26
        ]
    ]


def hill_process(text, matrix):

    s = clean_letters(text)

    if len(s) % 2 != 0:
        s += "X"

    result = []

    for i in range(0, len(s), 2):

        x1 = ord(s[i]) - 65
        x2 = ord(s[i + 1]) - 65

        y1 = (
            matrix[0][0] * x1 +
            matrix[0][1] * x2
        ) % 26

        y2 = (
            matrix[1][0] * x1 +
            matrix[1][1] * x2
        ) % 26

        result.append(chr(y1 + 65))
        result.append(chr(y2 + 65))

    return "".join(result)


def hill_encrypt(text, key):

    matrix = parse_hill_key(key)

    return hill_process(text, matrix)


def hill_decrypt(text, key):

    matrix = parse_hill_key(key)

    inverse = hill_inverse_matrix(matrix)

    return hill_process(text, inverse)


# ============================================================
# 5. VIGENERE CIPHER
# ============================================================

def validate_word_key(key):

    key = clean_letters(key)

    if not key:
        raise ValueError(
            "Key must contain at least one letter."
        )

    return key


def vigenere_encrypt(text, key):

    key = validate_word_key(key)

    index = 0
    result = []

    for ch in text:

        if ch.upper() in ALPHABET:

            shift = ord(
                key[index % len(key)]
            ) - 65

            base = 65 if ch.isupper() else 97

            result.append(
                chr(
                    (ord(ch) - base + shift) % 26
                    + base
                )
            )

            index += 1

        else:
            result.append(ch)

    return "".join(result)


def vigenere_decrypt(text, key):

    key = validate_word_key(key)

    index = 0
    result = []

    for ch in text:

        if ch.upper() in ALPHABET:

            shift = ord(
                key[index % len(key)]
            ) - 65

            base = 65 if ch.isupper() else 97

            result.append(
                chr(
                    (ord(ch) - base - shift) % 26
                    + base
                )
            )

            index += 1

        else:
            result.append(ch)

    return "".join(result)


# ============================================================
# 6. ONE-TIME PAD
# ============================================================

def otp_encrypt(text, key):

    key = validate_word_key(key)

    letter_count = sum(
        1 for ch in text
        if ch.upper() in ALPHABET
    )

    if len(key) != letter_count:
        raise ValueError(
            f"OTP key length must equal the number "
            f"of letters in plaintext ({letter_count})."
        )

    result = []
    index = 0

    for ch in text:

        if ch.upper() in ALPHABET:

            shift = ord(key[index]) - 65

            base = 65 if ch.isupper() else 97

            result.append(
                chr(
                    (ord(ch) - base + shift) % 26
                    + base
                )
            )

            index += 1

        else:
            result.append(ch)

    return "".join(result)


def otp_decrypt(text, key):

    key = validate_word_key(key)

    letter_count = sum(
        1 for ch in text
        if ch.upper() in ALPHABET
    )

    if len(key) != letter_count:
        raise ValueError(
            f"OTP key length must equal the number "
            f"of letters in ciphertext ({letter_count})."
        )

    result = []
    index = 0

    for ch in text:

        if ch.upper() in ALPHABET:

            shift = ord(key[index]) - 65

            base = 65 if ch.isupper() else 97

            result.append(
                chr(
                    (ord(ch) - base - shift) % 26
                    + base
                )
            )

            index += 1

        else:
            result.append(ch)

    return "".join(result)


def generate_otp_key(text):

    number_of_letters = sum(
        1 for ch in text
        if ch.upper() in ALPHABET
    )

    return "".join(
        random.choice(ALPHABET)
        for _ in range(number_of_letters)
    )


# ============================================================
# 7. RAIL FENCE CIPHER
# ============================================================

def display_rail_fence(text, rails):

    rails = int(rails)

    if rails < 2:
        print("Number of rails must be at least 2.")
        return

    if len(text) == 0:
        return

    # Create the visual matrix.
    fence = [
        [" " for _ in range(len(text))]
        for _ in range(rails)
    ]

    row = 0
    direction = 1

    # Place characters in zig-zag positions.
    for col, ch in enumerate(text):

        fence[row][col] = ch

        if row == 0:
            direction = 1

        elif row == rails - 1:
            direction = -1

        row += direction

    print("\nRail Fence Zig-Zag Pattern:")
    print("-" * (len(text) + 2))

    for row_data in fence:
        print("".join(row_data))

    print("-" * (len(text) + 2))


def rail_fence_encrypt(text, rails):

    rails = int(rails)

    if rails < 2:
        raise ValueError(
            "Number of rails must be at least 2."
        )

    if len(text) <= 1:
        return text

    fence = [[] for _ in range(rails)]

    row = 0
    direction = 1

    for ch in text:

        fence[row].append(ch)

        if row == 0:
            direction = 1

        elif row == rails - 1:
            direction = -1

        row += direction

    return "".join(
        "".join(r)
        for r in fence
    )


def rail_fence_decrypt(ciphertext, rails):

    rails = int(rails)

    if rails < 2:
        raise ValueError(
            "Number of rails must be at least 2."
        )

    if len(ciphertext) <= 1:
        return ciphertext

    pattern = []

    row = 0
    direction = 1

    for _ in ciphertext:

        pattern.append(row)

        if row == 0:
            direction = 1

        elif row == rails - 1:
            direction = -1

        row += direction

    counts = [
        pattern.count(r)
        for r in range(rails)
    ]

    rails_data = []

    index = 0

    for count in counts:

        rails_data.append(
            list(
                ciphertext[
                    index:index + count
                ]
            )
        )

        index += count

    positions = [0] * rails

    result = []

    for r in pattern:

        result.append(
            rails_data[r][positions[r]]
        )

        positions[r] += 1

    return "".join(result)


# ============================================================
# 8. COLUMNAR TRANSPOSITION CIPHER
# ============================================================

def column_order(key):

    key = validate_word_key(key)

    return sorted(
        range(len(key)),
        key=lambda i: (key[i], i)
    )


def display_columnar_table(text, key):

    key = validate_word_key(key)

    columns = len(key)

    rows = []

    for i in range(0, len(text), columns):
        rows.append(
            list(text[i:i + columns])
        )

    order = column_order(key)

    print("\nColumnar Transposition Table:")
    print("--------------------------------")

    print(" | ".join(key))
    print("--------------------------------")

    for row in rows:

        print(
            " | ".join(row) +
            (" |" if row else "")
        )

    print("--------------------------------")

    print(
        "Column reading order:",
        " -> ".join(
            str(i + 1)
            for i in order
        )
    )


def columnar_encrypt(text, key):

    key = validate_word_key(key)

    columns = len(key)

    rows = []

    for i in range(0, len(text), columns):
        rows.append(
            list(text[i:i + columns])
        )

    order = column_order(key)

    result = []

    for col in order:

        for row in rows:

            if col < len(row):
                result.append(row[col])

    return "".join(result)


def columnar_decrypt(ciphertext, key):

    key = validate_word_key(key)

    columns = len(key)

    n = len(ciphertext)

    full_rows = n // columns
    extra = n % columns

    col_lengths = [
        full_rows +
        (1 if col < extra else 0)
        for col in range(columns)
    ]

    column_data = [""] * columns

    index = 0

    for col in column_order(key):

        length = col_lengths[col]

        column_data[col] = ciphertext[
            index:index + length
        ]

        index += length

    positions = [0] * columns

    result = []

    for row in range(
        full_rows + (1 if extra else 0)
    ):

        for col in range(columns):

            if row < col_lengths[col]:

                result.append(
                    column_data[col][
                        positions[col]
                    ]
                )

                positions[col] += 1

    return "".join(result)


# ============================================================
# CIPHER INFORMATION
# ============================================================

CIPHERS = {
    1: "Caesar Cipher",
    2: "Monoalphabetic Cipher",
    3: "Playfair Cipher",
    4: "Hill Cipher",
    5: "Vigenere Cipher",
    6: "One-Time Pad",
    7: "Rail Fence Cipher",
    8: "Columnar Transposition Cipher",
}


# ============================================================
# USER INTERFACE
# ============================================================

def print_banner():

    print("\n" + "=" * 60)
    print(
        "             CLASSICAL CRYPTOGRAPHY TOOLKIT"
    )
    print("=" * 60)


def print_menu():

    print("\nSUBSTITUTION CIPHERS")
    print("1. Caesar Cipher")
    print("2. Monoalphabetic Cipher")
    print("3. Playfair Cipher")
    print("4. Hill Cipher")
    print("5. Vigenere (Polyalphabetic) Cipher")
    print("6. One-Time Pad")

    print("\nTRANSPOSITION CIPHERS")
    print("7. Rail Fence Cipher")
    print("8. Columnar Transposition Cipher")

    print("\nUTILITY MODULES")
    print("9. Compare Algorithms")
    print("10. Encrypt Text File")
    print("11. Decrypt Text File")
    print("12. Help")
    print("13. Exit")


# ============================================================
# GET KEYS
# ============================================================

def get_cipher_key(choice, text=None):

    if choice == 1:

        return int(
            input(
                "Enter numeric key (e.g. 5): "
            )
        )

    if choice == 2:

        print(
            "\nEnter a 26-letter substitution alphabet."
        )

        print(
            "Example:"
            " QWERTYUIOPASDFGHJKLZXCVBNM"
        )

        return input(
            "Enter substitution key: "
        )

    if choice == 3:

        return input(
            "Enter Playfair keyword: "
        )

    if choice == 4:

        print(
            "\nEnter 4 numbers for a 2x2 matrix."
        )

        print(
            "Example: 3 3 2 5"
        )

        return input(
            "Enter Hill key: "
        )

    if choice == 5:

        return input(
            "Enter Vigenere keyword: "
        )

    if choice == 6:

        if text is None:
            text = input(
                "Enter plaintext: "
            )

        print(
            "\nOTP requires a key with exactly "
            "the same number of letters as the text."
        )

        print(
            "Type RANDOM to generate a key automatically."
        )

        key = input(
            "Enter OTP key: "
        ).strip()

        if key.upper() == "RANDOM":

            key = generate_otp_key(text)

            print(
                "Generated OTP key:",
                key
            )

        return key

    if choice == 7:

        return int(
            input(
                "Enter number of rails (e.g. 3): "
            )
        )

    if choice == 8:

        return input(
            "Enter columnar keyword: "
        )

    return None


# ============================================================
# ENCRYPT / DECRYPT SELECTION
# ============================================================

def encrypt_with_choice(choice, text, key):

    if choice == 1:
        return caesar_encrypt(text, key)

    if choice == 2:
        return monoalphabetic_encrypt(text, key)

    if choice == 3:
        return playfair_encrypt(text, key)

    if choice == 4:
        return hill_encrypt(text, key)

    if choice == 5:
        return vigenere_encrypt(text, key)

    if choice == 6:
        return otp_encrypt(text, key)

    if choice == 7:
        return rail_fence_encrypt(text, key)

    if choice == 8:
        return columnar_encrypt(text, key)

    raise ValueError(
        "Invalid cipher choice."
    )


def decrypt_with_choice(choice, text, key):

    if choice == 1:
        return caesar_decrypt(text, key)

    if choice == 2:
        return monoalphabetic_decrypt(text, key)

    if choice == 3:
        return playfair_decrypt(text, key)

    if choice == 4:
        return hill_decrypt(text, key)

    if choice == 5:
        return vigenere_decrypt(text, key)

    if choice == 6:
        return otp_decrypt(text, key)

    if choice == 7:
        return rail_fence_decrypt(text, key)

    if choice == 8:
        return columnar_decrypt(text, key)

    raise ValueError(
        "Invalid cipher choice."
    )


# ============================================================
# RUN A CIPHER
# ============================================================

def run_cipher(choice):

    print(
        f"\n--- {CIPHERS[choice]} ---"
    )

    plaintext = input(
        "Enter Plaintext: "
    )

    key = get_cipher_key(
        choice,
        plaintext
    )

    # Show visual representation
    # for algorithms where it is useful.
    if choice == 3:
        display_playfair_square(key)

    elif choice == 4:
        display_hill_matrix(key)

    elif choice == 7:
        display_rail_fence(
            plaintext,
            key
        )

    elif choice == 8:
        display_columnar_table(
            plaintext,
            key
        )

    # Encryption timing
    start = time.perf_counter()

    ciphertext = encrypt_with_choice(
        choice,
        plaintext,
        key
    )

    encryption_time = (
        time.perf_counter() - start
    )

    # Decryption timing
    start = time.perf_counter()

    decrypted = decrypt_with_choice(
        choice,
        ciphertext,
        key
    )

    decryption_time = (
        time.perf_counter() - start
    )

    print("\nEncrypted Text :", ciphertext)

    print(
        "Decrypted Text :",
        decrypted
    )

    print(
        f"Encryption Time: "
        f"{encryption_time:.8f} seconds"
    )

    print(
        f"Decryption Time: "
        f"{decryption_time:.8f} seconds"
    )


# ============================================================
# COMPARE ALGORITHMS
# ============================================================

def compare_algorithms():

    print(
        "\n--- COMPARE ALGORITHMS ---"
    )

    text = input(
        "Enter plaintext: "
    )

    tests = [
        (1, 5),
        (
            2,
            "QWERTYUIOPASDFGHJKLZXCVBNM"
        ),
        (3, "SECURITY"),
        (4, "3 3 2 5"),
        (5, "KEY"),
        (7, 3),
        (8, "ZEBRA"),
    ]

    otp_key = generate_otp_key(text)

    tests.insert(
        5,
        (6, otp_key)
    )

    print(
        "\n{:<35} {:>16}".format(
            "Algorithm",
            "Time (seconds)"
        )
    )

    print("-" * 55)

    for choice, key in tests:

        try:

            start = time.perf_counter()

            encrypt_with_choice(
                choice,
                text,
                key
            )

            elapsed = (
                time.perf_counter() - start
            )

            print(
                "{:<35} {:>16.8f}".format(
                    CIPHERS[choice],
                    elapsed
                )
            )

        except Exception as e:

            print(
                "{:<35} ERROR: {}".format(
                    CIPHERS[choice],
                    e
                )
            )


# ============================================================
# FILE FUNCTIONS
# ============================================================

def choose_file_cipher():

    print(
        "\nChoose cipher for file operation:"
    )

    for number, name in CIPHERS.items():
        print(
            f"{number}. {name}"
        )

    choice = int(
        input(
            "Enter cipher choice: "
        )
    )

    if choice not in CIPHERS:
        raise ValueError(
            "Invalid cipher choice."
        )

    return choice


def encrypt_text_file():

    print(
        "\n--- ENCRYPT TEXT FILE ---"
    )

    input_name = input(
        "Enter input file path: "
    ).strip()

    output_name = input(
        "Enter output file path: "
    ).strip()

    path = Path(input_name)

    if not path.exists():
        raise FileNotFoundError(
            "Input file does not exist."
        )

    text = path.read_text(
        encoding="utf-8"
    )

    choice = choose_file_cipher()

    key = get_cipher_key(
        choice,
        text
    )

    encrypted = encrypt_with_choice(
        choice,
        text,
        key
    )

    Path(output_name).write_text(
        encrypted,
        encoding="utf-8"
    )

    print(
        f"\nEncrypted file saved as: "
        f"{output_name}"
    )

    print(
        "Use the same cipher and key "
        "during decryption."
    )


def decrypt_text_file():

    print(
        "\n--- DECRYPT TEXT FILE ---"
    )

    input_name = input(
        "Enter encrypted file path: "
    ).strip()

    output_name = input(
        "Enter output file path: "
    ).strip()

    path = Path(input_name)

    if not path.exists():
        raise FileNotFoundError(
            "Encrypted file does not exist."
        )

    text = path.read_text(
        encoding="utf-8"
    )

    choice = choose_file_cipher()

    if choice == 6:

        key = input(
            "Enter OTP key used during encryption: "
        )

    else:

        key = get_cipher_key(
            choice,
            text
        )

    decrypted = decrypt_with_choice(
        choice,
        text,
        key
    )

    Path(output_name).write_text(
        decrypted,
        encoding="utf-8"
    )

    print(
        f"\nDecrypted file saved as: "
        f"{output_name}"
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print_banner()

    while True:

        print_menu()

        try:

            choice = int(
                input(
                    "\nEnter your Choice: "
                )
            )

            if choice in CIPHERS:

                run_cipher(choice)

            elif choice == 9:

                compare_algorithms()

            elif choice == 10:

                encrypt_text_file()

            elif choice == 11:

                decrypt_text_file()

            elif choice == 12:

                help_menu()

            elif choice == 13:

                print(
                    "\nThank you for using "
                    "Classical Cryptography Toolkit."
                )

                print(
                    "Exiting..."
                )

                break

            else:

                print(
                    "Invalid choice. "
                    "Please select 1-13."
                )

        except ValueError as e:

            print(
                f"\nInput Error: {e}"
            )

        except FileNotFoundError as e:

            print(
                f"\nFile Error: {e}"
            )

        except Exception as e:

            print(
                f"\nError: {e}"
            )

        input(
            "\nPress Enter to return "
            "to the main menu..."
        )


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":
    main()
