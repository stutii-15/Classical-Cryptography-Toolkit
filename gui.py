import tkinter as tk
from tkinter import messagebox
import string
import random
import time

# ============================================================
# CLASSICAL CRYPTOGRAPHY TOOLKIT - COMPLETE GUI
# 8 working ciphers:
# Caesar, Monoalphabetic, Playfair, Hill, Vigenere, OTP,
# Rail Fence, Columnar Transposition
# ============================================================

ALPHABET = string.ascii_uppercase

BG = "#0b1220"
SIDEBAR = "#111827"
CARD = "#1e293b"
INPUT_BG = "#0f172a"
TEXT = "#f8fafc"
MUTED = "#94a3b8"
BLUE = "#2563eb"
BLUE_HOVER = "#1d4ed8"
GREEN = "#16a34a"
GREEN_HOVER = "#15803d"
GRAY = "#475569"


# ============================================================
# COMMON HELPERS
# ============================================================

def letters_only(text):
    return "".join(c for c in text.upper() if c in ALPHABET)


def require_letters(key, name="Key"):
    key = letters_only(key)
    if not key:
        raise ValueError(f"{name} must contain letters.")
    return key


def mod_inverse(a, m=26):
    a %= m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None


# ============================================================
# 1. CAESAR
# ============================================================

def caesar_encrypt(text, key):
    key = int(key) % 26
    out = []
    for ch in text:
        if ch.isupper():
            out.append(chr((ord(ch) - 65 + key) % 26 + 65))
        elif ch.islower():
            out.append(chr((ord(ch) - 97 + key) % 26 + 97))
        else:
            out.append(ch)
    return "".join(out)


def caesar_decrypt(text, key):
    return caesar_encrypt(text, -int(key))


# ============================================================
# 2. MONOALPHABETIC
# ============================================================

def mono_validate(key):
    key = letters_only(key)
    if len(key) != 26:
        raise ValueError(
            "Monoalphabetic key must contain exactly 26 letters."
        )
    if len(set(key)) != 26:
        raise ValueError(
            "Monoalphabetic key must contain 26 UNIQUE letters."
        )
    return key


def mono_encrypt(text, key):
    key = mono_validate(key)
    out = []
    for ch in text:
        if ch.isupper():
            out.append(key[ord(ch) - 65])
        elif ch.islower():
            out.append(key[ord(ch) - 65].lower())
        else:
            out.append(ch)
    return "".join(out)


def mono_decrypt(text, key):
    key = mono_validate(key)
    reverse = {key[i]: ALPHABET[i] for i in range(26)}
    out = []
    for ch in text:
        if ch.isupper():
            out.append(reverse[ch])
        elif ch.islower():
            out.append(reverse[ch.upper()].lower())
        else:
            out.append(ch)
    return "".join(out)


# ============================================================
# 3. PLAYFAIR
# ============================================================

def playfair_square(key):
    key = require_letters(key, "Playfair keyword").replace("J", "I")
    chars = []
    for ch in key + ALPHABET:
        if ch == "J":
            ch = "I"
        if ch not in chars:
            chars.append(ch)

    square = [chars[i:i+5] for i in range(0, 25, 5)]
    pos = {}
    for r in range(5):
        for c in range(5):
            pos[square[r][c]] = (r, c)
    pos["J"] = pos["I"]
    return square, pos


def playfair_pairs(text):
    s = letters_only(text).replace("J", "I")
    pairs = []
    i = 0
    while i < len(s):
        a = s[i]
        if i + 1 >= len(s):
            pairs.append(a + "X")
            i += 1
        elif s[i + 1] == a:
            pairs.append(a + "X")
            i += 1
        else:
            pairs.append(a + s[i + 1])
            i += 2
    return pairs


def playfair_transform_pair(a, b, square, pos, encrypt=True):
    ra, ca = pos[a]
    rb, cb = pos[b]
    step = 1 if encrypt else -1

    if ra == rb:
        return (
            square[ra][(ca + step) % 5],
            square[rb][(cb + step) % 5],
        )

    if ca == cb:
        return (
            square[(ra + step) % 5][ca],
            square[(rb + step) % 5][cb],
        )

    return square[ra][cb], square[rb][ca]


def playfair_encrypt(text, key):
    square, pos = playfair_square(key)
    out = []
    for pair in playfair_pairs(text):
        a, b = playfair_transform_pair(
            pair[0], pair[1], square, pos, True
        )
        out.extend([a, b])
    return "".join(out)


def playfair_decrypt(text, key):
    square, pos = playfair_square(key)
    s = letters_only(text).replace("J", "I")
    if len(s) % 2:
        s += "X"

    out = []
    for i in range(0, len(s), 2):
        a, b = playfair_transform_pair(
            s[i], s[i+1], square, pos, False
        )
        out.extend([a, b])
    return "".join(out)


# ============================================================
# 4. HILL 2x2
# ============================================================

def hill_inverse(matrix):
    a, b = matrix[0]
    c, d = matrix[1]

    det = (a*d - b*c) % 26
    inv_det = mod_inverse(det)

    if inv_det is None:
        raise ValueError(
            "Invalid Hill matrix. Determinant has no inverse modulo 26."
        )

    return [
        [(d * inv_det) % 26, (-b * inv_det) % 26],
        [(-c * inv_det) % 26, (a * inv_det) % 26],
    ]


def hill_process(text, matrix):
    s = letters_only(text)
    if not s:
        return ""

    if len(s) % 2:
        s += "X"

    out = []
    for i in range(0, len(s), 2):
        x1 = ord(s[i]) - 65
        x2 = ord(s[i+1]) - 65

        y1 = (matrix[0][0] * x1 + matrix[0][1] * x2) % 26
        y2 = (matrix[1][0] * x1 + matrix[1][1] * x2) % 26

        out.append(chr(y1 + 65))
        out.append(chr(y2 + 65))

    return "".join(out)


def hill_encrypt(text, matrix):
    return hill_process(text, matrix)


def hill_decrypt(text, matrix):
    return hill_process(text, hill_inverse(matrix))


# ============================================================
# 5. VIGENERE
# ============================================================

def vigenere_encrypt(text, key):
    key = require_letters(key, "Vigenere keyword")
    out = []
    i = 0

    for ch in text:
        if ch.upper() in ALPHABET:
            shift = ord(key[i % len(key)]) - 65
            base = 65 if ch.isupper() else 97
            out.append(chr((ord(ch) - base + shift) % 26 + base))
            i += 1
        else:
            out.append(ch)

    return "".join(out)


def vigenere_decrypt(text, key):
    key = require_letters(key, "Vigenere keyword")
    out = []
    i = 0

    for ch in text:
        if ch.upper() in ALPHABET:
            shift = ord(key[i % len(key)]) - 65
            base = 65 if ch.isupper() else 97
            out.append(chr((ord(ch) - base - shift) % 26 + base))
            i += 1
        else:
            out.append(ch)

    return "".join(out)


# ============================================================
# 6. ONE-TIME PAD
# ============================================================

def generate_otp_key(text):
    n = len(letters_only(text))
    if n == 0:
        raise ValueError("Enter text before generating an OTP key.")
    return "".join(random.choice(ALPHABET) for _ in range(n))


def otp_process(text, key, decrypt=False):
    key = letters_only(key)
    needed = len(letters_only(text))

    if needed == 0:
        raise ValueError("Input must contain letters.")

    if len(key) != needed:
        raise ValueError(
            f"OTP key must contain exactly {needed} letters."
        )

    out = []
    i = 0

    for ch in text:
        if ch.upper() in ALPHABET:
            shift = ord(key[i]) - 65
            if decrypt:
                shift = -shift
            base = 65 if ch.isupper() else 97
            out.append(chr((ord(ch) - base + shift) % 26 + base))
            i += 1
        else:
            out.append(ch)

    return "".join(out)


# ============================================================
# 7. RAIL FENCE
# ============================================================

def rail_encrypt(text, rails):
    rails = int(rails)
    if rails < 2:
        raise ValueError("Number of rails must be at least 2.")
    if len(text) <= 1:
        return text

    fence = [[] for _ in range(rails)]
    row, direction = 0, 1

    for ch in text:
        fence[row].append(ch)
        if row == 0:
            direction = 1
        elif row == rails - 1:
            direction = -1
        row += direction

    return "".join("".join(r) for r in fence)


def rail_decrypt(ciphertext, rails):
    rails = int(rails)
    if rails < 2:
        raise ValueError("Number of rails must be at least 2.")
    if len(ciphertext) <= 1:
        return ciphertext

    pattern = []
    row, direction = 0, 1

    for _ in ciphertext:
        pattern.append(row)
        if row == 0:
            direction = 1
        elif row == rails - 1:
            direction = -1
        row += direction

    counts = [pattern.count(r) for r in range(rails)]
    rails_data = []
    index = 0

    for count in counts:
        rails_data.append(list(ciphertext[index:index+count]))
        index += count

    positions = [0] * rails
    out = []

    for r in pattern:
        out.append(rails_data[r][positions[r]])
        positions[r] += 1

    return "".join(out)


def rail_visual(text, rails):
    fence = [[" " for _ in range(len(text))] for _ in range(rails)]
    row, direction = 0, 1

    for col, ch in enumerate(text):
        fence[row][col] = ch
        if row == 0:
            direction = 1
        elif row == rails - 1:
            direction = -1
        row += direction

    return "\n".join("".join(r) for r in fence)


# ============================================================
# 8. COLUMNAR TRANSPOSITION
# ============================================================

def column_order(key):
    key = require_letters(key, "Columnar keyword")
    return sorted(range(len(key)), key=lambda i: (key[i], i))


def columnar_encrypt(text, key):
    key = require_letters(key, "Columnar keyword")
    # Spaces are removed for classical columnar transposition.
    s = letters_only(text)
    if not s:
        return ""

    cols = len(key)
    rows = [s[i:i+cols] for i in range(0, len(s), cols)]

    out = []
    for col in column_order(key):
        for row in rows:
            if col < len(row):
                out.append(row[col])

    return "".join(out)


def columnar_decrypt(ciphertext, key):
    key = require_letters(key, "Columnar keyword")
    s = letters_only(ciphertext)
    cols = len(key)

    if not s:
        return ""

    full_rows = len(s) // cols
    extra = len(s) % cols

    lengths = [
        full_rows + (1 if c < extra else 0)
        for c in range(cols)
    ]

    columns = [""] * cols
    index = 0

    for col in column_order(key):
        length = lengths[col]
        columns[col] = s[index:index+length]
        index += length

    positions = [0] * cols
    out = []

    for row in range(full_rows + (1 if extra else 0)):
        for col in range(cols):
            if row < lengths[col]:
                out.append(columns[col][positions[col]])
                positions[col] += 1

    return "".join(out)


def columnar_visual(text, key):
    key = require_letters(key, "Columnar keyword")
    s = letters_only(text)
    cols = len(key)
    rows = [s[i:i+cols] for i in range(0, len(s), cols)]

    lines = [
        "COLUMNAR TRANSPOSITION",
        "Keyword : " + key,
        "Order   : " + " -> ".join(
            str(i+1) for i in column_order(key)
        ),
        "-" * max(25, cols * 4),
        " | ".join(key)
    ]

    for row in rows:
        padded = row.ljust(cols)
        lines.append(" | ".join(padded))

    return "\n".join(lines)


# ============================================================
# GUI
# ============================================================

CIPHERS = [
    "Caesar Cipher",
    "Monoalphabetic Cipher",
    "Playfair Cipher",
    "Hill Cipher",
    "Vigenere Cipher",
    "One-Time Pad",
    "Rail Fence Cipher",
    "Columnar Transposition",
]

root = tk.Tk()
root.title("Classical Cryptography Toolkit")
root.geometry("1200x800")
root.minsize(1000, 700)
root.configure(bg=BG)

selected = tk.StringVar(value="Caesar Cipher")
status = tk.StringVar(value="Ready")
timing = tk.StringVar(value="")

# ---------------- HEADER ----------------

header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=28, pady=(18, 8))

tk.Label(
    header,
    text="🔐 CLASSICAL CRYPTOGRAPHY TOOLKIT",
    font=("Segoe UI", 24, "bold"),
    fg=TEXT,
    bg=BG,
).pack()

tk.Label(
    header,
    text="Encryption • Decryption • Classical Ciphers",
    font=("Segoe UI", 11),
    fg=MUTED,
    bg=BG,
).pack(pady=(4, 0))

# ---------------- CONTENT ----------------

content = tk.Frame(root, bg=BG)
content.pack(fill="both", expand=True, padx=28, pady=10)

sidebar = tk.Frame(content, bg=SIDEBAR, width=285)
sidebar.pack(side="left", fill="y", padx=(0, 18))
sidebar.pack_propagate(False)

work = tk.Frame(content, bg=CARD)
work.pack(side="left", fill="both", expand=True)

# ---------------- SIDEBAR ----------------

tk.Label(
    sidebar,
    text="CIPHERS",
    font=("Segoe UI", 18, "bold"),
    fg=TEXT,
    bg=SIDEBAR,
).pack(anchor="w", padx=20, pady=(20, 18))


def select_cipher(name):
    selected.set(name)
    selected_label.config(text=f"Selected Cipher: {name}")
    result_box.delete("1.0", "end")
    visual_box.delete("1.0", "end")
    status.set(f"{name} selected")
    timing.set("")
    build_key_area()


def make_button(name):
    tk.Button(
        sidebar,
        text=name,
        font=("Segoe UI", 10),
        fg=TEXT,
        bg=SIDEBAR,
        activebackground=BLUE_HOVER,
        activeforeground="white",
        relief="flat",
        bd=0,
        anchor="w",
        padx=20,
        pady=5,
        cursor="hand2",
        command=lambda n=name: select_cipher(n),
    ).pack(fill="x")


tk.Label(
    sidebar,
    text="SUBSTITUTION",
    font=("Segoe UI", 10, "bold"),
    fg=MUTED,
    bg=SIDEBAR,
).pack(anchor="w", padx=20, pady=(8, 4))

for name in CIPHERS[:6]:
    make_button(name)

tk.Label(
    sidebar,
    text="TRANSPOSITION",
    font=("Segoe UI", 10, "bold"),
    fg=MUTED,
    bg=SIDEBAR,
).pack(anchor="w", padx=20, pady=(18, 4))

for name in CIPHERS[6:]:
    make_button(name)

# ---------------- WORKSPACE HEADER ----------------

tk.Label(
    work,
    text="ENCRYPTION / DECRYPTION",
    font=("Segoe UI", 19, "bold"),
    fg=TEXT,
    bg=CARD,
).pack(anchor="w", padx=28, pady=(22, 5))

selected_label = tk.Label(
    work,
    text="Selected Cipher: Caesar Cipher",
    font=("Segoe UI", 11),
    fg=BLUE,
    bg=CARD,
)
selected_label.pack(anchor="w", padx=28, pady=(0, 10))

# ---------------- INPUT ----------------

tk.Label(
    work,
    text="INPUT TEXT (PLAINTEXT / CIPHERTEXT)",
    font=("Segoe UI", 10, "bold"),
    fg=MUTED,
    bg=CARD,
).pack(anchor="w", padx=28)

input_box = tk.Text(
    work,
    height=5,
    font=("Consolas", 11),
    bg=INPUT_BG,
    fg=TEXT,
    insertbackground=TEXT,
    relief="flat",
    padx=12,
    pady=10,
)
input_box.pack(fill="x", padx=28, pady=(5, 10))

# ---------------- KEY AREA ----------------

tk.Label(
    work,
    text="KEY",
    font=("Segoe UI", 10, "bold"),
    fg=MUTED,
    bg=CARD,
).pack(anchor="w", padx=28)

key_area = tk.Frame(work, bg=CARD)
key_area.pack(fill="x", padx=28, pady=(4, 10))

key_entry = None
hill_entries = []


def clear_key_area():
    global key_entry, hill_entries
    for w in key_area.winfo_children():
        w.destroy()
    key_entry = None
    hill_entries = []


def single_key(label_text):
    global key_entry

    tk.Label(
        key_area,
        text=label_text,
        font=("Segoe UI", 9),
        fg=MUTED,
        bg=CARD,
    ).pack(anchor="w")

    key_entry = tk.Entry(
        key_area,
        font=("Consolas", 11),
        bg=INPUT_BG,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat",
    )
    key_entry.pack(fill="x", pady=(3, 0))


def hill_key():
    global hill_entries

    tk.Label(
        key_area,
        text="Enter the four matrix values",
        font=("Segoe UI", 9),
        fg=MUTED,
        bg=CARD,
    ).pack(anchor="w")

    frame = tk.Frame(key_area, bg=CARD)
    frame.pack(anchor="w", pady=3)

    hill_entries = []

    for r in range(2):
        row = []
        for c in range(2):
            e = tk.Entry(
                frame,
                width=8,
                justify="center",
                font=("Consolas", 11),
                bg=INPUT_BG,
                fg=TEXT,
                insertbackground=TEXT,
                relief="flat",
            )
            e.grid(row=r, column=c, padx=4, pady=3)
            row.append(e)
        hill_entries.append(row)


def otp_key():
    global key_entry

    single_key("OTP key - same number of letters as input")

    tk.Button(
        key_area,
        text="Generate Random OTP Key",
        font=("Segoe UI", 9, "bold"),
        bg=BLUE,
        fg="white",
        activebackground=BLUE_HOVER,
        relief="flat",
        cursor="hand2",
        command=generate_otp,
    ).pack(anchor="w", pady=(4, 0))


def generate_otp():
    text = input_box.get("1.0", "end").strip()
    try:
        key = generate_otp_key(text)
        key_entry.delete(0, "end")
        key_entry.insert(0, key)
        status.set("Random OTP key generated")
    except Exception as e:
        messagebox.showerror("OTP", str(e))


def build_key_area():
    clear_key_area()
    cipher = selected.get()

    if cipher == "Caesar Cipher":
        single_key("Integer shift key")

    elif cipher == "Monoalphabetic Cipher":
        single_key("26-letter UNIQUE substitution alphabet")

    elif cipher == "Playfair Cipher":
        single_key("Keyword")

    elif cipher == "Hill Cipher":
        hill_key()

    elif cipher == "Vigenere Cipher":
        single_key("Alphabetic keyword")

    elif cipher == "One-Time Pad":
        otp_key()

    elif cipher == "Rail Fence Cipher":
        single_key("Number of rails (integer >= 2)")

    elif cipher == "Columnar Transposition":
        single_key("Alphabetic keyword")


# ---------------- ACTION BUTTONS ----------------

actions = tk.Frame(work, bg=CARD)
actions.pack(fill="x", padx=28, pady=(0, 10))

tk.Button(
    actions,
    text="🔒  ENCRYPT",
    font=("Segoe UI", 10, "bold"),
    bg=GREEN,
    fg="white",
    activebackground=GREEN_HOVER,
    relief="flat",
    padx=25,
    pady=9,
    cursor="hand2",
    command=lambda: process(True),
).pack(side="left", padx=(0, 10))

tk.Button(
    actions,
    text="🔓  DECRYPT",
    font=("Segoe UI", 10, "bold"),
    bg=BLUE,
    fg="white",
    activebackground=BLUE_HOVER,
    relief="flat",
    padx=25,
    pady=9,
    cursor="hand2",
    command=lambda: process(False),
).pack(side="left", padx=(0, 10))

tk.Button(
    actions,
    text="CLEAR",
    font=("Segoe UI", 10, "bold"),
    bg=GRAY,
    fg="white",
    activebackground="#334155",
    relief="flat",
    padx=25,
    pady=9,
    cursor="hand2",
    command=lambda: clear_all(),
).pack(side="left")

# ---------------- RESULT ----------------

tk.Label(
    work,
    text="RESULT",
    font=("Segoe UI", 10, "bold"),
    fg=MUTED,
    bg=CARD,
).pack(anchor="w", padx=28)

result_box = tk.Text(
    work,
    height=4,
    font=("Consolas", 11),
    bg=INPUT_BG,
    fg="#22c55e",
    insertbackground=TEXT,
    relief="flat",
    padx=12,
    pady=8,
)
result_box.pack(fill="x", padx=28, pady=(5, 8))

# ---------------- VISUALIZATION ----------------

tk.Label(
    work,
    text="VISUALIZATION",
    font=("Segoe UI", 10, "bold"),
    fg=MUTED,
    bg=CARD,
).pack(anchor="w", padx=28)

visual_box = tk.Text(
    work,
    height=7,
    font=("Consolas", 10),
    bg=INPUT_BG,
    fg="#60a5fa",
    insertbackground=TEXT,
    relief="flat",
    padx=12,
    pady=8,
)
visual_box.pack(fill="both", expand=True, padx=28, pady=(5, 6))

# ---------------- STATUS ----------------

status_frame = tk.Frame(work, bg=CARD)
status_frame.pack(fill="x", padx=28, pady=(2, 8))

tk.Label(
    status_frame,
    textvariable=status,
    font=("Segoe UI", 9),
    fg="#22c55e",
    bg=CARD,
).pack(side="left")

tk.Label(
    status_frame,
    textvariable=timing,
    font=("Segoe UI", 9),
    fg=MUTED,
    bg=CARD,
).pack(side="right")


# ============================================================
# KEY READING
# ============================================================

def get_key():
    cipher = selected.get()

    if cipher == "Hill Cipher":
        if len(hill_entries) != 2:
            raise ValueError("Enter the Hill matrix.")

        values = []
        for row in hill_entries:
            for e in row:
                raw = e.get().strip()
                if not raw:
                    raise ValueError(
                        "Fill all four Hill matrix values."
                    )
                values.append(int(raw) % 26)

        return [
            [values[0], values[1]],
            [values[2], values[3]],
        ]

    if key_entry is None:
        raise ValueError("Enter the key.")

    raw = key_entry.get().strip()

    if not raw:
        raise ValueError("Key cannot be empty.")

    if cipher == "Caesar Cipher":
        return int(raw)

    if cipher == "Rail Fence Cipher":
        rails = int(raw)
        if rails < 2:
            raise ValueError("Number of rails must be at least 2.")
        return rails

    return raw


# ============================================================
# VISUALIZATION
# ============================================================

def show_visualization(cipher, text, key, encrypted):
    visual_box.delete("1.0", "end")

    if cipher == "Caesar Cipher":
        visual_box.insert(
            "end",
            f"Caesar shift = {int(key) % 26}\n"
            f"Example: A -> {chr((65 + int(key)) % 26 + 65)}"
        )

    elif cipher == "Monoalphabetic Cipher":
        k = mono_validate(key)
        visual_box.insert(
            "end",
            "MONOALPHABETIC MAPPING\n"
            + "Plain : " + ALPHABET + "\n"
            + "Key   : " + k
        )

    elif cipher == "Playfair Cipher":
        square, _ = playfair_square(key)
        lines = [
            "PLAYFAIR 5 x 5 KEY MATRIX",
            "-" * 25
        ]
        lines += ["  ".join(row) for row in square]
        visual_box.insert("end", "\n".join(lines))

    elif cipher == "Hill Cipher":
        m = key
        visual_box.insert(
            "end",
            "HILL 2 x 2 KEY MATRIX\n"
            "----------------------\n"
            f"| {m[0][0]:2}  {m[0][1]:2} |\n"
            f"| {m[1][0]:2}  {m[1][1]:2} |"
        )

    elif cipher == "Vigenere Cipher":
        k = require_letters(key)
        clean = letters_only(text)
        repeated = (k * ((len(clean) // len(k)) + 1))[:len(clean)]
        visual_box.insert(
            "end",
            "VIGENERE KEY ALIGNMENT\n"
            f"Text : {clean}\n"
            f"Key  : {repeated}"
        )

    elif cipher == "One-Time Pad":
        visual_box.insert(
            "end",
            "ONE-TIME PAD\n"
            "Plain/Cipher letters are combined with the random key.\n"
            f"OTP Key: {letters_only(key)}"
        )

    elif cipher == "Rail Fence Cipher":
        visual_box.insert(
            "end",
            "RAIL FENCE ZIG-ZAG\n"
            + "-" * 30 + "\n"
            + rail_visual(text, key)
        )

    elif cipher == "Columnar Transposition":
        visual_box.insert(
            "end",
            columnar_visual(text, key)
        )


# ============================================================
# ENCRYPT / DECRYPT
# ============================================================

def process(encrypt_mode):
    cipher = selected.get()

    # IMPORTANT:
    # Encrypt always uses INPUT TEXT.
    # Decrypt automatically uses the previous RESULT if it exists.
    # This prevents accidentally decrypting the original plaintext.
    input_text = input_box.get("1.0", "end").rstrip("\n")
    previous_result = result_box.get("1.0", "end").rstrip("\n")

    if encrypt_mode:
        text = input_text
    else:
        # If encryption was just performed, decrypt its result.
        # Otherwise, allow the user to type ciphertext into INPUT TEXT.
        text = previous_result if previous_result.strip() else input_text

    if not text.strip():
        messagebox.showwarning(
            "Missing Input",
            "Enter plaintext/ciphertext in INPUT TEXT first."
        )
        return

    try:
        key = get_key()
        start = time.perf_counter()

        if cipher == "Caesar Cipher":
            result = caesar_encrypt(text, key) if encrypt_mode else caesar_decrypt(text, key)

        elif cipher == "Monoalphabetic Cipher":
            result = mono_encrypt(text, key) if encrypt_mode else mono_decrypt(text, key)

        elif cipher == "Playfair Cipher":
            result = playfair_encrypt(text, key) if encrypt_mode else playfair_decrypt(text, key)

        elif cipher == "Hill Cipher":
            result = hill_encrypt(text, key) if encrypt_mode else hill_decrypt(text, key)

        elif cipher == "Vigenere Cipher":
            result = vigenere_encrypt(text, key) if encrypt_mode else vigenere_decrypt(text, key)

        elif cipher == "One-Time Pad":
            result = otp_process(text, key, decrypt=not encrypt_mode)

        elif cipher == "Rail Fence Cipher":
            result = rail_encrypt(text, key) if encrypt_mode else rail_decrypt(text, key)

        elif cipher == "Columnar Transposition":
            result = columnar_encrypt(text, key) if encrypt_mode else columnar_decrypt(text, key)

        else:
            raise ValueError("Unknown cipher.")

        elapsed = time.perf_counter() - start

        result_box.delete("1.0", "end")
        result_box.insert("end", result)

        visual_box.delete("1.0", "end")
        show_visualization(cipher, text, key, result)

        if encrypt_mode:
            status.set("Encryption successful")
        else:
            status.set("Decryption successful")

        timing.set(f"Time: {elapsed:.8f} sec")

    except Exception as e:
        result_box.delete("1.0", "end")
        visual_box.delete("1.0", "end")
        status.set("Operation failed")
        timing.set("")
        messagebox.showerror("Operation Error", str(e))


# ============================================================
# CLEAR
# ============================================================

def clear_all():
    input_box.delete("1.0", "end")
    result_box.delete("1.0", "end")
    visual_box.delete("1.0", "end")
    status.set("Ready")
    timing.set("")

    # Clear key fields without inserting defaults.
    for e in hill_entries:
        for field in e:
            field.delete(0, "end")

    if key_entry is not None:
        key_entry.delete(0, "end")


# Initial state
build_key_area()

root.mainloop()
