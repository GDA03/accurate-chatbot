import pypdf

reader = pypdf.PdfReader("../data/MODUL PEMBELAJARAN.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

print(f"Total karakter: {len(text)}")
print(f"Kata 'produk': {text.lower().count('produk')}")
print(f"Kata 'accurate': {text.lower().count('accurate')}")
print(f"Kata 'mereka': {text.lower().count('mereka')}")

if "produk" in text.lower():
    import re
    # Print the lines containing 'produk'
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if 'produk' in line.lower() or 'accurate' in line.lower() and i < 20:
            print(f"Line {i}: {line.strip()}")
