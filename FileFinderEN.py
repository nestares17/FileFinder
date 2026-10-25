import json
import os
import queue
import string
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk

VERSION = "Version 1.0"
BLUE = "#1976D2"
DARK_BLUE = "#1259A5"
WHITE = "#FFFFFF"
LIGHT_BLUE = "#E8F1FB"
SELECTION_BLUE = "#D6E8FA"
SELECTION_TEXT_BLUE = "#0D47A1"
TEXT_GRAY = "#2B3340"
SOFT_GRAY = "#7A869A"
BORDER_GRAY = "#D5DCE5"
LINE_GRAY = "#EDF0F4"

SCREEN_PERCENT = 0.20
THREADS = 16
INCLUDE_FOLDERS = False
IGNORE = {"$recycle.bin", "system volume information", "winsxs", "node_modules", ".git"}

UI_TIME = 0.012
FORBIDDEN_SYMBOLS = '*?"<>|' if os.name == "nt" else ""
BOX_WIDTH = 0.60
DUCK_SPEED = 140

DUCK_FRAMES = [
    (
        "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAcCAYAAAB2+A+pAAABEElEQVR42tWWzQ2DMAyF/VAWYALGCEdG50jGYAJG"
        "eD0Ul/DTkIIjVEscEgl/if1sB6Q8YpXIH4EBuR0nXA01ICQF20OQgqLgBc7NHrLglSX0EXEBmEPNlQYA4ZEmnBV4"
        "H/I3bOqbeT0yToErUSoKS4baojTOrO7GneCgabEUl+Y7VWLuTi2mc5724Y7EAYC/iulXcyWcXgZ/zxXLgzE347O9"
        "4/9utEydAKVuXFkKKPe2jz4EPmPxzrRZBkR+/a/mcdxIcg5xBXj6EMjt4Ve7XJUzZdR5vNav6EMAECp06hsBhG3r"
        "2baeZg1kcRZ2o03Ne1+mc4UQJL6hgmPgMASYg733Undht2cBTKp6mzsrWGwvGtOfhz3YmY0AAAAASUVORK5CYII="
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAcCAYAAAB2+A+pAAABDklEQVR42tVWwQ2DMAy8Q1mACTqG++zoPGGMTtAR"
        "ro8SAYFAIIlQLVkII3KJffaFEm6xBvgzYBJZuWJOqklIAsNNSGBV4AlcQYyH4E1p0FvIRXJMtRYcIKGwHK4k8Drl"
        "P7BP9xjf3/IlcLXaxYPtpjq3NVKsfb0XhKM0tUVJcvl6x1rM+eCVXjyueXwNFyMHSZ0l0xlzNRbNAo7XSvWBObLu"
        "KLb9X8bI9ApQ48RNaQKlnPbWi8BCFnPUZhKItP5f6fF8kKRs4ixg0kUgdYZfmXKHNfYq458SGHpRVj+fplBdfDz8"
        "dnWQr9zMBECf7rFwAAIgM9PWf2c8OrnMDO1r2IwXb6e9VM+t7wdWA65tX3VgzT7WSq/YAAAAAElFTkSuQmCC"
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAcCAYAAAB2+A+pAAABEElEQVR42tWWzQ2DMAyF/VAWYALGCEdG50jGYAJG"
        "eD0Ul/DTkIIjVEscEgl/if1sB6Q8YpXIH4EBuR0nXA01ICQF20OQgqLgBc7NHrLglSX0EXEBmEPNlQYA4ZEmnBV4"
        "H/I3bOqbeT0yToErUSoKS4baojTOrO7GneCgabEUl+Y7VWLuTi2mc5724Y7EAYC/iulXcyWcXgZ/zxXLgzE347O9"
        "4/9utEydAKVuXFkKKPe2jz4EPmPxzrRZBkR+/a/mcdxIcg5xBXj6EMjt4Ve7XJUzZdR5vNav6EMAECp06hsBhG3r"
        "2baeZg1kcRZ2o03Ne1+mc4UQJL6hgmPgMASYg733Undht2cBTKp6mzsrWGwvGtOfhz3YmY0AAAAASUVORK5CYII="
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAcCAYAAAB2+A+pAAABBElEQVR42u2WzRGEIAyF8xgasALLwKOle5QyrMAS"
        "socVf5AFhDBeNidlRj9IXvIAM70SiugPTgdA1QVCaY0BYmaCvwlmQlPwAWdvDVlwJQl9RVwAtlTzRQMAcUgTWgp8"
        "T/kXtk799r7wuQS6Ras4WDTVEq2Rim5cboKDK4ukuFy9Yy2ma3oxXvP4P3RIHAD4qZiehm7x02Lw71pxezC2YZxa"
        "C39XMTKdA7Q6sZIUUO5pX70I7LZY4zaHQeT3/8WPz4MkZxMlwORFIHeGl045lesy7tkYQ8YYYibUjNYgeBgMhxxm"
        "nXqy1sqKy0+z76nduOwnJiKaZwtxcKjGDigBrb5l1sQHrg6SspOWpvMAAAAASUVORK5CYII="
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAcCAYAAAB2+A+pAAABCUlEQVR42u2WzRGEIAyF8xwasALLCEdL9yhlWIEl"
        "ZA8L6w8uooRxD5ubzOAHyUseEKFHoiH6g38YDFCxMnBXXACJCGF/CBFCVfACl90asuCNJvQRcQHwqZaNBgCSI00Y"
        "LXCc8jdsHjr/Pcm6BKZGqwRYMtUarXEWbT9FgkMoi6a4Qr1TLWZKejFd8/Q/zJE4AMhVMV0NU+Ont8HfayX1wfDD"
        "+GzteF/ByAwOUOvGjaaAcm/76EPgY4slbrMYRH7/b/x4PUhyDnEHePoQyJ3hd6dc1E7Wsgc6moeO2n7auE7bT8TM"
        "qx1O581lLYtzLrK2cIAAHUcH9QHCzNT2LlrTACZrvKSbVGHreAHkMZJvlSQeKQAAAABJRU5ErkJggg=="
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAcCAYAAAB2+A+pAAABEElEQVR42tVWQQ6EIAzsED7gC3wGHH26R3mGL/AJ"
        "3cPKisIiCyVmm5goiQydTjuAmR4JRfRHwAA184RaqgFiZsL1EMyErsAHOF/WUASuJEEfEReAnWo+aQAgTmlCSwHH"
        "lL/Btnncv1cOS6B7tIoHy1It0Rp3MUxrJDj4skiKy9c712K6pRfzNc/voVPiAMC/iunX0D02rQb+XivuD4x9GN+t"
        "pf9rGJneAXplrCQFVJrtoxeBjy22uM1hEOX9f/LjcJCUHKIG8PYiUDrDa6ecKnUZ/85MCJ8uAyQV1poTE8viZDK2"
        "1vB1c29t2zySc05W1SGwcy4y82FaiYjIGNOUaZZqYwwNk4vWJACzqpaqYy5ei42g0STNl70AAAAASUVORK5CYII="
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAcCAYAAAB2+A+pAAABC0lEQVR42s1X2w2DMAz0oSzABB0jPBm9TzIGE3SE"
        "6+NEIaEBQxLRWkIIP3Lx+ewDpNwSncifAQNSxBVKqAaEpCC9BCloChzAmeRwCN7VBr1FXAAWqhlpABCm7TA1gbeU"
        "f8Bez8fyPdO3wLQaFw+2S3XpaGiiH+dIcCDDWNQUl+93bsSMT16ZxeOe588wOXEA4FkxnQnT4tCfNglzZjFo2dCs"
        "TKMBbUF7V1tAmmpv7XFkiyVuEwxCN/8bP14vEs0lzgKqfgS0O/zKljvssXcZ/yYF6VN1jofBUsRF7hLyIabJoVhc"
        "64OdcxtP9eDW2mLgbMXWWulH9zVfAqjaXOvKSitUqbpWH/fiDT0Bmc79I/KUAAAAAElFTkSuQmCC"
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAcCAYAAAB2+A+pAAABGElEQVR42sVX2w2EMAyzEQswAWMcn4zOJzcGEzCC"
        "7wPK8WpJoRWRokqlinHiJkAJr1iRIgiJ6NcvU7LYv4AEes+mSjUJaReMpBe8yAFK8vSM8+Sp/qdYy0pSADB2NQCg"
        "agdkA16bAzyk+o4i71rVDkvNKbkaTVqwqnKvZHlUuq73Ol7pNjyqlLWe4TNHAuXToOFsMG/nimW7AZ7SzcdMLM3j"
        "wNgCPovhcSbKWIYW0Cu2p8Az643ClWF2eofE2fWyZsZ0/0OxY5qDFdA8FkMtNQYo6h6TkGvybpVA508v+KkD0NjV"
        "Wq++s3f8snONXY2qHTB2NVJOMqO4lr7B7MBN8zk86ftvMuDCChraz8o4Jdukn7ev/EncsR/F29RCgJWZbAAAAABJ"
        "RU5ErkJggg=="
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAcCAYAAAB2+A+pAAABHElEQVR42sVXWxKDIAzMMl7AE9hb1E+Pbv/sMTyB"
        "vcH2ByhteUSFNjMMDjLZbFgSBSl/MVPDCSC7w0ctxoCQFMSCIAXNgF/gjKzjC9y0BAVgGdPvcRnpWgooDAQQbvNg"
        "n1ealil29rhdxIH6VB9R5Bnrp1VIAci0ImNqTF2lHGN31qFPr+qcOLTnmAKNEejOOC1nA20rVz74+HGZcIMmtdoj"
        "SKU4ylgDDqvEs9btZagBLbGNAlvWbwpng96ZbBKlapTLjOr+53yXisOnHjSA6raYK6l7gHbd47CjuJkUuHH2gkeH"
        "iHCbB4Zzau+RUaxc2zxIP62yzYPU7GRKcfm6gebA43j9erMs92rARguaW2/KuCbb6p+3P/+TOGJPmWTduNB1sDkA"
        "AAAASUVORK5CYII="
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAcCAYAAAB2+A+pAAABHUlEQVR42tVWwQ2DMAy8Q12ACegW9Mno9EfHYAK6"
        "wfVRQmlxQoCkVSNFQSjy+eyzHUr4ySpSGCGx2X2mYkxCEmg5IYHZgF/gMv5zAV7kBCU5MtZ0x0XklFNAc0dIaGir"
        "8btXkTPEbt2vZzjQKdR7FHlklU0PCaTkV6SlRl8phRi7XM9tTqoOiSM2jz5Qi8DpiNH1aDBv5wo7b6frrYGE1Pnp"
        "/d4Qm6F+CoxmrpV4mhSxjSBGaLFsTeCRdXKhRQ+JtW4U0kFU/YdsrzWHpeDAw4xjhvwWoE3imk8Ud0qg20cL3NwA"
        "NLSV5qfv7p69Wk5DW6FsegxthaSTLOQVAAFQXdfJGXvFdbnUXnZdd+NXOtdX39U+VinYJn/e/kWoH3B5EJQHm6E9"
        "AAAAAElFTkSuQmCC"
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAcCAYAAAB2+A+pAAABHElEQVR42sVXWxKDIAzMMl7AE9hb1E+Pbv/sMTyB"
        "vcH2ByhteUSFNjMMDjLZbFgSBSl/MVPDCSC7w0ctxoCQFMSCIAXNgF/gjKzjC9y0BAVgGdPvcRnpWgooDAQQbvNg"
        "n1ealil29rhdxIH6VB9R5Bnrp1VIAci0ImNqTF2lHGN31qFPr+qcOLTnmAKNEejOOC1nA20rVz74+HGZcIMmtdoj"
        "SKU4ylgDDqvEs9btZagBLbGNAlvWbwpng96ZbBKlapTLjOr+53yXisOnHjSA6raYK6l7gHbd47CjuJkUuHH2gkeH"
        "iHCbB4Zzau+RUaxc2zxIP62yzYPU7GRKcfm6gebA43j9erMs92rARguaW2/KuCbb6p+3P/+TOGJPmWTduNB1sDkA"
        "AAAASUVORK5CYII="
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAcCAYAAAB2+A+pAAABHUlEQVR42tVWwQ2DMAy8Q12ACegW9Mno9EfHYAK6"
        "wfVRQmlxQoCkVSNFQSjy+eyzHUr4ySpSGCGx2X2mYkxCEmg5IYHZgF/gMv5zAV7kBCU5MtZ0x0XklFNAc0dIaGir"
        "8btXkTPEbt2vZzjQKdR7FHlklU0PCaTkV6SlRl8phRi7XM9tTqoOiSM2jz5Qi8DpiNH1aDBv5wo7b6frrYGE1Pnp"
        "/d4Qm6F+CoxmrpV4mhSxjSBGaLFsTeCRdXKhRQ+JtW4U0kFU/YdsrzWHpeDAw4xjhvwWoE3imk8Ud0qg20cL3NwA"
        "NLSV5qfv7p69Wk5DW6FsegxthaSTLOQVAAFQXdfJGXvFdbnUXnZdd+NXOtdX39U+VinYJn/e/kWoH3B5EJQHm6E9"
        "AAAAAElFTkSuQmCC"
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAcCAYAAAB2+A+pAAABGElEQVR42sVX2w2EMAyzEQswAWMcn4zOJzcGEzCC"
        "7wPK8WpJoRWRokqlinHiJkAJr1iRIgiJ6NcvU7LYv4AEes+mSjUJaReMpBe8yAFK8vSM8+Sp/qdYy0pSADB2NQCg"
        "agdkA16bAzyk+o4i71rVDkvNKbkaTVqwqnKvZHlUuq73Ol7pNjyqlLWe4TNHAuXToOFsMG/nimW7AZ7SzcdMLM3j"
        "wNgCPovhcSbKWIYW0Cu2p8Az643ClWF2eofE2fWyZsZ0/0OxY5qDFdA8FkMtNQYo6h6TkGvybpVA508v+KkD0NjV"
        "Wq++s3f8snONXY2qHTB2NVJOMqO4lr7B7MBN8zk86ftvMuDCChraz8o4Jdukn7ev/EncsR/F29RCgJWZbAAAAABJ"
        "RU5ErkJggg=="
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAcCAYAAAB2+A+pAAABFElEQVR42sWWzY3DIBCF37PoIBW4jMkxpfuYlJEK"
        "XMLbw8ZZ7CV4jBllpJEMFnwwv1BCs5CQBDatPQPO4SRWO+0d6DT4D67NHKvwIQLqkQGdheTL1EJufhLKx6k3+L/J"
        "P7BP9xjf3/IlcLXaxYPtpjq3NVKsfb0XhKM0tUVJcvl6x1rM+eCVXjyueXwNFyMHSZ0l0xlzNRbNAo7XSvWBObLu"
        "KLb9X8bI9ApQ48RNaQKlnPbWi8BCFnPUZhKItP5f6fF8kKRs4ixg0kUgdYZfmXKHNfYq458SGHpRVj+fplBdfDz8"
        "dnWQr9zMBECf7rFwAAIgM9PWf2c8OrnMDO1r2IwXb6e9VM+t7wdWA65tX3VgzT7WSq/YAAAAAElFTkSuQmCC"
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAcCAYAAAB2+A+pAAABCElEQVR42tVWwQ2DMAz0oSzABB0jPBm9TzIGE3SE"
        "6+NEIaEBQxLRWkIIP3Lx+ewDpNwSncifAQNSxBVKqAaEpCC9BCloChzAmeRwCN7VBr1FXAAWqhlpABCm7TA1gbeU"
        "f8Bez8fyPdO3wLQaFw+2S3XpaGiiH+dIcCDDWNQUl+93bsSMT16ZxeOe588wOXEA4FkxnQnT4tCfNglzZjFo2dCs"
        "TKMBbUF7V1tAmmpv7XFkiyVuEwxCN/8bP14vEs0lzgKqfgS0O/zKljvssXcZ/yYF6VN1jofBUsRF7hLyIabJoVhc"
        "64OdcxtP9eDW2mLgbMXWWulH9zVfAqjaXOvKSitUqbpWH/fiDT0Bmc79I/KUAAAAAElFTkSuQmCC"
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAcCAYAAAB2+A+pAAABDUlEQVR42u2WwRGEIAxF8x0asALLwKOle5QyrMAS"
        "soeVRVA0Ghgvm9tmXB/k/ySCmV6JhugPlgVAKpGg0RggZiakh2AmVAUHOCc5XMKb0tBXzAVgLTVHHgCIUzlMSfC+"
        "5F/YMnbr75m9BKZWu3jYaam1rSGJdpgjw4E5tEVJc3m9cy1mfPJJL15rnn+HyZkDAN81050wNV6qAue14vpgrK67"
        "yh3/TzEy/QaoceOmtIEkt331QyBai5ptExaErP93+3g7SCSHuAsUfQhIZ/iTKZdtp763TORoGTtqh/mXt9ZGz02T"
        "g1rjACRyzu1Wmz/AFv4UnL2xtZbawR3mNUDR5ErLWgJ4ai5f7tKwbXwAZviWASIyTz4AAAAASUVORK5CYII="
    ),
]


DUCK_ICON = (
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAABXUlEQVR42u2ZWw6DIBBFoekGXEGXwa9L76/LcAVd"
    "wvSnJEJUqK8Z9dzEL4hB7pkH4hxCCCGE0HGS32NCj7u74ZVJGK5BNNYKAUZyghOZB8B7v8uab0/A07rzVIGrV4Ep"
    "AmLM5+MzuUCWfBs5wGy7WM4NyYTP+5UMNm0vNSRAwNkWnDtNFdiQgKqYsa6m7akCS/uAowlY1AkO+oBNehtywMjO"
    "qZzLtbpYCPi3E/Peb3J80z4FQsDSTtCKcxBg5SxQqsvWiYGAtc7X/s1dSwJ/ha0REB0tOUwOuHoV2NvhvWIfAtgA"
    "NqAYVyp3dyOdpYcAJQISEvbK/kc7DgEb7rYYWgsEqHWC8a5u5EZGCuP0AZcgYCo35Le4AxLEOedCCMl413XkANME"
    "hBAkc2x2/iDm8/dwFjh1DojOT8V4TsCU41oxDwFrCYiONm1XNc+a4xCwtv/Oq4HV2IYAhBCq0BdEkXf+Oc+pLQAA"
    "AABJRU5ErkJggg=="
)


def history_path():
    base = os.environ.get("APPDATA") if os.name == "nt" else None
    if not base:
        base = os.path.expanduser("~")
    return os.path.join(base, "FileFinder", "search_history.json")


def format_number(n):
    return f"{n:,}"


def get_roots():
    if os.name == "nt":
        return [f"{l}:\\" for l in string.ascii_uppercase if os.path.exists(f"{l}:\\")]
    return [os.path.expanduser("~")]


def search(query, roots, results, stop, n_threads=THREADS):
    by_path = any(c in query for c in "/\\:")
    if by_path:
        query = query.replace("\\", "/")

    pending = queue.Queue()
    for r in roots:
        pending.put(r)

    def worker():
        get = pending.get
        put = pending.put
        finish = pending.task_done
        scandir = os.scandir
        send = results.put
        ignore = IGNORE
        include_folders = INCLUDE_FOLDERS
        while True:
            folder = get()
            if folder is None:
                return
            try:
                if not stop.is_set():
                    base = folder.replace("\\", "/").lower().rstrip("/") if by_path else ""
                    found = []
                    add = found.append
                    with scandir(folder) as it:
                        for e in it:
                            name = e.name.lower()
                            try:
                                if e.is_dir(follow_symlinks=False):
                                    if name not in ignore:
                                        put(e.path)
                                    if not include_folders:
                                        continue
                                if by_path:
                                    if query in f"{base}/{name}":
                                        add(e.path)
                                elif query in name:
                                    add(e.path)
                            except OSError:
                                pass
                    if found:
                        send(found)
            except OSError:
                pass
            finally:
                finish()

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(n_threads)]
    for t in threads:
        t.start()
    pending.join()
    for _ in threads:
        pending.put(None)
    results.put(None)


def open_path(path):
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as ex:
        messagebox.showerror("FileFinder", f"Could not open:\n{ex}")


def open_folder(path):
    try:
        if sys.platform.startswith("win"):
            subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
        else:
            open_path(os.path.dirname(path))
    except Exception as ex:
        messagebox.showerror("FileFinder", f"Could not open the folder:\n{ex}")


def _rounded_rect(c, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return c.create_polygon(pts, smooth=True, **kw)


class RoundedButton(tk.Canvas):
    def __init__(self, master, text, command, solid=True,
                 font=("Segoe UI", 10, "bold"), padx=20, pady=7):
        f = tkfont.Font(font=font)
        w = f.measure(text) + 2 * padx
        h = f.metrics("linespace") + 2 * pady
        super().__init__(master, width=w, height=h, bg=WHITE,
                         highlightthickness=0, bd=0)
        self._command = command
        self._solid = solid
        self._active = True
        self._hover = False
        self._background = _rounded_rect(self, 1, 1, w - 1, h - 1, 9, width=1)
        self._txt = self.create_text(w / 2, h / 2, text=text, font=font)
        self._paint()
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self.bind("<ButtonRelease-1>", self._release)

    def _set_hover(self, value):
        self._hover = value
        self._paint()

    def _release(self, _e):
        if self._active and self._hover:
            self._command()

    def enable(self, active):
        self._active = active
        self._paint()

    def _paint(self):
        if not self._active:
            if self._solid:
                bg, border, fg = "#BBD7F5", "#BBD7F5", WHITE
            else:
                bg, border, fg = WHITE, LINE_GRAY, "#B0B8C4"
        elif self._solid:
            bg = border = DARK_BLUE if self._hover else BLUE
            fg = WHITE
        else:
            bg = LIGHT_BLUE if self._hover else WHITE
            border, fg = BLUE, BLUE
        self.itemconfig(self._background, fill=bg, outline=border)
        self.itemconfig(self._txt, fill=fg)
        self.configure(cursor="hand2" if self._active else "arrow")


class RoundedField(tk.Canvas):
    def __init__(self, master, width=400, height=40, font=("Segoe UI", 11)):
        super().__init__(master, width=width, height=height, bg=WHITE,
                         highlightthickness=0, bd=0)
        self._height = height
        self._focus = False
        self.entry = tk.Entry(self, font=font, relief="flat", bd=0, bg=WHITE,
                              fg=TEXT_GRAY, insertbackground=BLUE,
                              highlightthickness=0)
        self._win = self.create_window(14, height / 2, window=self.entry, anchor="w")
        self.bind("<Configure>", self._draw)
        self.bind("<Button-1>", lambda e: self.entry.focus_set())
        self.entry.bind("<FocusIn>", lambda e: self._set_focus(True), add="+")
        self.entry.bind("<FocusOut>", lambda e: self._set_focus(False), add="+")

    def _set_focus(self, value):
        self._focus = value
        self._draw()

    def _draw(self, _e=None):
        w = self.winfo_width()
        if w < 10:
            return
        self.delete("background")
        _rounded_rect(self, 2, 2, w - 2, self._height - 2, 10, tags="background",
                      fill=WHITE, outline=BLUE if self._focus else BORDER_GRAY,
                      width=2 if self._focus else 1)
        self.tag_lower("background")
        self.itemconfig(self._win, width=w - 28)


_scroll_styles = set()


def create_scrollbar(parent, orientation, command=None):
    base = "Vertical" if orientation == "vertical" else "Horizontal"
    name = f"Thin.{base}.TScrollbar"
    try:
        if name not in _scroll_styles:
            style = ttk.Style(parent)
            style.theme_use("clam")
            style.layout(name, [(f"{base}.Scrollbar.trough", {
                "sticky": "ns" if base == "Vertical" else "ew",
                "children": [(f"{base}.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})],
            })])
            style.configure(name, background="#D3E1F2", troughcolor=WHITE,
                            bordercolor=WHITE, lightcolor="#D3E1F2", darkcolor="#D3E1F2",
                            relief="flat", width=10, arrowsize=10)
            style.map(name,
                      background=[("pressed", DARK_BLUE), ("active", BLUE)],
                      lightcolor=[("pressed", DARK_BLUE), ("active", BLUE)],
                      darkcolor=[("pressed", DARK_BLUE), ("active", BLUE)])
            _scroll_styles.add(name)
        return ttk.Scrollbar(parent, orient=orientation, style=name, command=command)
    except tk.TclError:
        return tk.Scrollbar(parent, orient=orientation, command=command)


class VirtualList(tk.Frame):
    def __init__(self, master, on_change=None, on_activate=None, on_menu=None):
        super().__init__(master, bg=WHITE)
        self.items = []
        self.sel = None
        self.top = 0
        self.x = 0
        self.on_change = on_change
        self.on_activate = on_activate
        self.on_menu = on_menu

        self._font = tkfont.Font(font=("Segoe UI", 10))
        self._row_height = self._font.metrics("linespace") + 6
        self._max_width = 0
        self._pending = None
        self._texts = []

        self.canvas = tk.Canvas(self, bg=WHITE, bd=0, highlightthickness=1,
                                highlightbackground=LINE_GRAY,
                                highlightcolor=LINE_GRAY, takefocus=1)
        self._sb_y = create_scrollbar(self, "vertical", self._yview)
        self._sb_x = create_scrollbar(self, "horizontal", self._xview)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self._sb_y.grid(row=0, column=1, sticky="ns")
        self._sb_x.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._sel_rect = self.canvas.create_rectangle(
            0, 0, 0, 0, fill=SELECTION_BLUE, outline="", state="hidden")

        c = self.canvas
        c.bind("<Configure>", lambda e: self.redraw())
        c.bind("<Button-1>", self._click)
        c.bind("<Double-Button-1>", self._double)
        c.bind("<Button-3>", self._right)
        for key in ("<Up>", "<Down>", "<Prior>", "<Next>",
                    "<Home>", "<End>", "<Return>", "<KP_Enter>"):
            c.bind(key, self._key)
        c.bind("<Enter>", self._enable_wheel)
        c.bind("<Leave>", self._disable_wheel)

    def set_items(self, data):
        self.items = list(data)
        self.sel = None
        self.top = 0
        self.x = 0
        self._max_width = 0
        self.redraw()
        self._notify()

    def extend(self, data):
        self.items.extend(data)
        if self._pending is None:
            self._pending = self.after_idle(self._deferred_redraw)

    def get_selection(self):
        if self.sel is not None and self.sel < len(self.items):
            return self.items[self.sel]
        return None

    def clear_selection(self):
        self.sel = None
        self.redraw()
        self._notify()

    def select(self, i, show=True):
        self.sel = i
        if show:
            visible = self._visible_rows()
            if i < self.top:
                self.top = i
            elif i >= self.top + visible:
                self.top = i - visible + 1
        self.redraw()
        self._notify()

    def _notify(self):
        if self.on_change:
            self.on_change()

    def _visible_rows(self):
        return max(1, self.canvas.winfo_height() // self._row_height)

    def _total_width(self):
        return max(self.canvas.winfo_width(), self._max_width + 24)

    def _deferred_redraw(self):
        self._pending = None
        self.redraw()

    def redraw(self):
        c = self.canvas
        width, height = c.winfo_width(), c.winfo_height()
        if width < 10 or height < 10:
            return

        n = len(self.items)
        rows = max(1, height // self._row_height)
        self.top = max(0, min(self.top, n - rows))

        first = self.top
        last = min(n, first + rows + 1)
        visible = self.items[first:last]

        measure = self._font.measure
        for t in visible:
            w = measure(t)
            if w > self._max_width:
                self._max_width = w
        total_w = self._total_width()
        self.x = max(0, min(self.x, total_w - width))

        while len(self._texts) < rows + 1:
            self._texts.append(c.create_text(0, 0, anchor="w", font=self._font,
                                             fill=TEXT_GRAY, state="hidden"))
        for k, tid in enumerate(self._texts):
            if k < len(visible):
                i = first + k
                c.itemconfigure(tid, text=visible[k], state="normal",
                                fill=SELECTION_TEXT_BLUE if i == self.sel else TEXT_GRAY)
                c.coords(tid, 10 - self.x, k * self._row_height + self._row_height / 2)
            else:
                c.itemconfigure(tid, state="hidden")

        if self.sel is not None and first <= self.sel < last:
            y0 = (self.sel - first) * self._row_height
            c.coords(self._sel_rect, 0, y0, width, y0 + self._row_height)
            c.itemconfigure(self._sel_rect, state="normal")
        else:
            c.itemconfigure(self._sel_rect, state="hidden")
        c.tag_lower(self._sel_rect)

        if n:
            self._sb_y.set(first / n, min(n, first + rows) / n)
        else:
            self._sb_y.set(0, 1)
        self._sb_x.set(self.x / total_w, min(1, (self.x + width) / total_w))

    def _yview(self, action, value, unit=None):
        n = len(self.items)
        if action == "moveto":
            self.top = int(float(value) * n)
        else:
            step = max(1, self._visible_rows() - 1) if unit == "pages" else 3
            self.top += int(value) * step
        self.redraw()

    def _xview(self, action, value, unit=None):
        if action == "moveto":
            self.x = int(float(value) * self._total_width())
        else:
            step = max(20, self.canvas.winfo_width() - 40) if unit == "pages" else 30
            self.x += int(value) * step
        self.redraw()

    def _wheel(self, e):
        if e.num == 4:
            direction = -1
        elif e.num == 5:
            direction = 1
        else:
            direction = -1 if e.delta > 0 else 1
        if e.state & 0x0001:
            self.x += direction * 40
        else:
            self.top += direction * 3
        self.redraw()

    def _enable_wheel(self, _e=None):
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.bind_all(seq, self._wheel)

    def _disable_wheel(self, _e=None):
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.unbind_all(seq)

    def _index_at(self, y):
        i = self.top + y // self._row_height
        return i if 0 <= i < len(self.items) else None

    def _click(self, e):
        self.canvas.focus_set()
        i = self._index_at(e.y)
        if i is not None:
            self.select(i, show=False)

    def _double(self, e):
        i = self._index_at(e.y)
        if i is not None:
            self.select(i, show=False)
            if self.on_activate:
                self.on_activate()

    def _right(self, e):
        i = self._index_at(e.y)
        if i is not None:
            self.select(i, show=False)
            if self.on_menu:
                self.on_menu(e)

    def _key(self, e):
        n = len(self.items)
        if not n:
            return
        if e.keysym in ("Return", "KP_Enter"):
            if self.sel is not None and self.on_activate:
                self.on_activate()
            return
        page = max(1, self._visible_rows() - 1)
        current = -1 if self.sel is None else self.sel
        target = {
            "Up": current - 1, "Down": current + 1,
            "Prior": current - page, "Next": current + page,
            "Home": 0, "End": n - 1,
        }.get(e.keysym)
        if target is not None:
            self.select(min(max(target, 0), n - 1))


class FileFinder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FileFinder")
        self.configure(bg=WHITE)
        try:
            self._icon = tk.PhotoImage(data=DUCK_ICON)
            self.iconphoto(True, self._icon)
        except tk.TclError:
            pass
        self._center()
        self.resizable(False, False)

        self.results_queue = queue.Queue()
        self.stop = threading.Event()
        self.search_id = 0
        self.total = 0
        self.history_mode = False
        self.history = self._load_history()

        self.top_spacer = tk.Frame(self, bg=WHITE, height=0)
        self.top_spacer.pack()

        self.header = tk.Frame(self, bg=WHITE)
        self.header.pack(pady=(0, 8))
        self.logo = tk.Frame(self.header, bg=WHITE, cursor="hand2")
        self.logo_file = tk.Label(self.logo, text="File", font=("Segoe UI", 26, "bold"),
                                  fg=BLUE, bg=WHITE, cursor="hand2")
        self.logo_file.pack(side="left")
        self.logo_finder = tk.Label(self.logo, text="Finder.", font=("Segoe UI", 26, "bold"),
                                    fg=TEXT_GRAY, bg=WHITE, cursor="hand2")
        self.logo_finder.pack(side="left")
        self.logo.pack(side="left")
        self.duck = tk.Label(self.header, bg=WHITE, cursor="hand2", bd=0)
        self.duck.pack(side="left", padx=(12, 0))
        for logo_part in (self.logo, self.logo_file, self.logo_finder):
            logo_part.bind("<Button-1>", self._go_home)
        self.duck.bind("<Button-1>", self._go_home)
        self._load_duck()

        self.field = RoundedField(self, width=min(int(self.window_width * BOX_WIDTH), 520))
        self.field.pack(pady=(4, 12))
        self.entry = self.field.entry
        self.placeholder = "Enter the name of the file you are looking for"
        self.placeholder_visible = True
        self.entry.insert(0, self.placeholder)
        self.entry.config(fg="#9AA5B1")
        self.entry.bind("<FocusIn>", self._remove_placeholder, add="+")
        self.entry.bind("<FocusOut>", self._put_placeholder, add="+")
        self.entry.bind("<KeyPress>", self._remove_placeholder, add="+")
        self.entry.bind("<Return>", lambda e: self.start_search())

        self.button_frame = tk.Frame(self, bg=WHITE)
        self.button_frame.pack(pady=(0, 12))
        RoundedButton(self.button_frame, "Search", self.start_search,
                      solid=True, padx=30).pack(side="left", padx=(0, 8))
        RoundedButton(self.button_frame, "Search history",
                      self.show_history, solid=False,
                      padx=18).pack(side="left")

        self.results_panel = tk.Frame(self, bg=WHITE)
        tk.Frame(self.results_panel, height=1, bg=LINE_GRAY).pack(fill="x", padx=26)

        self.status = tk.Label(self.results_panel, text="", font=("Segoe UI", 9),
                               fg=SOFT_GRAY, bg=WHITE, anchor="w")
        self.status.pack(fill="x", padx=26, pady=(8, 5))

        bar = tk.Frame(self.results_panel, bg=WHITE)
        bar.pack(side="bottom", fill="x", padx=26, pady=(4, 16))
        self.action_buttons = []
        for text, command in (
            ("Open file", self._open_selection),
            ("Open containing folder", self._open_selected_folder),
            ("Copy path", self._copy_path),
        ):
            b = RoundedButton(bar, text, command, solid=False,
                              font=("Segoe UI", 9), padx=12, pady=5)
            b.pack(side="left", padx=(0, 6))
            b.enable(False)
            self.action_buttons.append(b)

        self.listbox = VirtualList(self.results_panel,
                                   on_change=self._on_change,
                                   on_activate=self._on_activate,
                                   on_menu=self._show_menu)
        self.listbox.pack(fill="both", expand=True, padx=26, pady=(0, 4))

        tk.Label(self, text=VERSION, font=("Segoe UI", 8), fg=SOFT_GRAY,
                 bg=WHITE, bd=0).place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-6)

        self.bind("<Escape>", self._deselect)

        self.menu = tk.Menu(self, tearoff=0, bg=WHITE, fg=TEXT_GRAY,
                            activebackground=BLUE, activeforeground=WHITE,
                            relief="flat", bd=1)
        self.menu.add_command(label="Open file", command=self._open_selection)
        self.menu.add_command(label="Open containing folder", command=self._open_selected_folder)
        self.menu.add_command(label="Copy path", command=self._copy_path)

        self._start_mode(True)

    def _center(self):
        pw, ph = self.winfo_screenwidth(), self.winfo_screenheight()
        factor = SCREEN_PERCENT ** 0.5
        w = max(int(pw * factor), 520)
        h = max(int(ph * factor), 460)
        x, y = (pw - w) // 2, (ph - h) // 2
        self.window_width, self.window_height = w, h
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _load_duck(self):
        self.duck_frames = []
        originals = []
        for i, data in enumerate(DUCK_FRAMES):
            try:
                originals.append(tk.PhotoImage(data=data))
            except tk.TclError as ex:
                print(f"FileFinder: duck frame {i} is not valid: {ex}", file=sys.stderr)

        if not originals:
            self.duck.pack_forget()
            return

        try:
            target = self.winfo_fpixels("26p") * 1.15
            height = originals[0].height()
            a, b = min(((a, b) for b in (1, 2) for a in range(1, 25)),
                       key=lambda ab: (abs(ab[0] / ab[1] * height - target), ab[1]))
            for f in originals:
                f = f.zoom(a) if a > 1 else f
                self.duck_frames.append(f.subsample(b) if b > 1 else f)
        except tk.TclError:
            self.duck_frames = originals

        self.duck.config(image=self.duck_frames[0])
        self._animate_duck()

    def _animate_duck(self, i=0):
        self.duck.config(image=self.duck_frames[i])
        self.after(DUCK_SPEED, self._animate_duck, (i + 1) % len(self.duck_frames))

    def _start_mode(self, start):
        if start:
            self.update_idletasks()
            content = (self.header.winfo_reqheight() + 8 +
                       self.field.winfo_reqheight() + 16 +
                       self.button_frame.winfo_reqheight() + 12)
            height = max(0, (self.window_height - content) // 2 - 16)
        else:
            height = 14
        self.top_spacer.config(height=max(height, 1))

    def _show_results_view(self):
        if not self.results_panel.winfo_manager():
            self._start_mode(False)
            self.results_panel.pack(fill="both", expand=True)

    def _remove_placeholder(self, _event=None):
        if self.placeholder_visible:
            self.entry.delete(0, "end")
            self.entry.config(fg=TEXT_GRAY)
            self.placeholder_visible = False

    def _put_placeholder(self, _event=None):
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg="#9AA5B1")
            self.placeholder_visible = True

    def _cancel_search(self):
        self.stop.set()
        self.search_id += 1

    def _go_home(self, _event=None):
        self._cancel_search()
        self.history_mode = False
        self.listbox.set_items([])
        self.results_panel.pack_forget()
        self._start_mode(True)
        self.entry.delete(0, "end")
        self.placeholder_visible = False
        self._put_placeholder()
        self.status.config(text="")
        self.total = 0

    def start_search(self):
        if self.placeholder_visible:
            self._message("Type something to search.")
            return
        text = self.entry.get()
        text = (text if text and not text.strip() else text.strip()).lower()
        if not text:
            self._message("Type something to search.")
            return
        forbidden = [c for c in FORBIDDEN_SYMBOLS if c in text]
        if forbidden:
            self._message(f"Windows does not allow {' '.join(forbidden)} in file names, "
                          "so there can be no matches.")
            return
        self._search_text(text)

    def _message(self, text):
        self._show_results_view()
        self._cancel_search()
        self.history_mode = False
        self.listbox.set_items([])
        self.status.config(text=text)

    def _search_text(self, text):
        self._show_results_view()
        self.entry.delete(0, "end")
        self.entry.insert(0, text)
        self.entry.config(fg=TEXT_GRAY)
        self.placeholder_visible = False
        self._add_to_history(text)
        self.history_mode = False

        self._cancel_search()
        my_id = self.search_id
        self.stop = threading.Event()
        self.results_queue = queue.Queue()
        self.total = 0
        self.listbox.set_items([])
        self.status.config(text="Searching...")

        threading.Thread(target=search,
                         args=(text, get_roots(), self.results_queue, self.stop),
                         daemon=True).start()
        self.after(20, self._read_queue, my_id, self.results_queue)

    def _read_queue(self, my_id, results_queue):
        if my_id != self.search_id:
            return
        done = False
        limit = time.perf_counter() + UI_TIME
        while time.perf_counter() < limit:
            try:
                item = results_queue.get_nowait()
            except queue.Empty:
                break
            if item is None:
                done = True
                break
            self.listbox.extend(item)
            self.total += len(item)

        if done:
            self.status.config(
                text=f"{format_number(self.total)} result{'s' if self.total != 1 else ''}")
        else:
            self.status.config(text=f"Searching... {format_number(self.total)} found")
            self.after(30, self._read_queue, my_id, results_queue)

    def show_history(self):
        self._show_results_view()
        self._cancel_search()
        self.history_mode = True
        self.listbox.set_items(self.history)
        if self.history:
            n = len(self.history)
            self.status.config(text=f"{n} search{'es' if n != 1 else ''} in history")
        else:
            self.status.config(text="There are no searches in the history yet.")

    def _load_history(self):
        path = history_path()
        try:
            with open(path, "r", encoding="utf-8") as history_file:
                history = json.load(history_file)
            if not isinstance(history, list) or not all(
                isinstance(term, str) for term in history
            ):
                raise ValueError("The history format is not valid.")
            return history
        except FileNotFoundError:
            return []
        except (OSError, json.JSONDecodeError, ValueError) as ex:
            messagebox.showerror(
                "FileFinder", f"Could not load the history:\n{ex}"
            )
            return []

    def _add_to_history(self, term):
        if not term.strip():
            return
        self.history = [term] + [
            previous for previous in self.history if previous != term
        ]
        path = history_path()
        temp = path + ".tmp"
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(temp, "w", encoding="utf-8") as history_file:
                json.dump(self.history, history_file, ensure_ascii=False, indent=2)
            os.replace(temp, path)
        except OSError as ex:
            messagebox.showerror(
                "FileFinder", f"Could not save the history:\n{ex}"
            )

    def _update_buttons(self, active):
        for b in self.action_buttons:
            b.enable(active)

    def _on_change(self):
        self._update_buttons(not self.history_mode and self.listbox.sel is not None)

    def _on_activate(self):
        if self.history_mode:
            term = self.listbox.get_selection()
            if term:
                self._search_text(term)
        else:
            self._open_selection()

    def _deselect(self, _event=None):
        self.listbox.clear_selection()

    def _selection(self):
        return None if self.history_mode else self.listbox.get_selection()

    def _open_selection(self, _event=None):
        path = self._selection()
        if path:
            open_path(path)

    def _open_selected_folder(self):
        path = self._selection()
        if path:
            open_folder(path)

    def _copy_path(self):
        path = self._selection()
        if path:
            self.clipboard_clear()
            self.clipboard_append(path)

    def _show_menu(self, event):
        if self.history_mode or not self.listbox.items:
            return
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()


if __name__ == "__main__":
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    sys.setswitchinterval(0.002)
    FileFinder().mainloop()