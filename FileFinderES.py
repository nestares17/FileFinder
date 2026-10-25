"""
FileFinder - Buscador rápido de archivos
Requisitos: Python 3.8+ (tkinter viene incluido en el instalador de Python para Windows)
Ejecutar:   python filefinder.py
"""

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

VERSION = "Versión 1.0"
AZUL = "#1976D2"
AZUL_OSCURO = "#1259A5"
BLANCO = "#FFFFFF"
AZUL_CLARO = "#E8F1FB"
AZUL_SELECCION = "#D6E8FA"
AZUL_TEXTO_SEL = "#0D47A1"
GRIS_TEXTO = "#2B3340"
GRIS_SUAVE = "#7A869A"
GRIS_BORDE = "#D5DCE5"
GRIS_LINEA = "#EDF0F4"

PORCENTAJE_PANTALLA = 0.20
HILOS = 16
INCLUIR_CARPETAS = False
IGNORAR = {"$recycle.bin", "system volume information", "winsxs", "node_modules", ".git"}

TIEMPO_UI = 0.012
SIMBOLOS_PROHIBIDOS = '*?"<>|' if os.name == "nt" else ""
ANCHO_CAJA = 0.60
VELOCIDAD_PATO = 140

PATO_FRAMES = [
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


PATO_ICONO = (
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAABXUlEQVR42u2ZWw6DIBBFoekGXEGXwa9L76/LcAVd"
    "wvSnJEJUqK8Z9dzEL4hB7pkH4hxCCCGE0HGS32NCj7u74ZVJGK5BNNYKAUZyghOZB8B7v8uab0/A07rzVIGrV4Ep"
    "AmLM5+MzuUCWfBs5wGy7WM4NyYTP+5UMNm0vNSRAwNkWnDtNFdiQgKqYsa6m7akCS/uAowlY1AkO+oBNehtywMjO"
    "qZzLtbpYCPi3E/Peb3J80z4FQsDSTtCKcxBg5SxQqsvWiYGAtc7X/s1dSwJ/ha0REB0tOUwOuHoV2NvhvWIfAtgA"
    "NqAYVyp3dyOdpYcAJQISEvbK/kc7DgEb7rYYWgsEqHWC8a5u5EZGCuP0AZcgYCo35Le4AxLEOedCCMl413XkANME"
    "hBAkc2x2/iDm8/dwFjh1DojOT8V4TsCU41oxDwFrCYiONm1XNc+a4xCwtv/Oq4HV2IYAhBCq0BdEkXf+Oc+pLQAA"
    "AABJRU5ErkJggg=="
)


def ruta_historial():
    """Devuelve la ubicación persistente del historial de búsquedas."""
    base = os.environ.get("APPDATA") if os.name == "nt" else None
    if not base:
        base = os.path.expanduser("~")
    return os.path.join(base, "FileFinder", "search_history.json")


def formato_numero(n):
    return f"{n:,}".replace(",", ".")


def obtener_raices():
    """Devuelve las carpetas/unidades donde buscar."""
    if os.name == "nt":
        return [f"{l}:\\" for l in string.ascii_uppercase if os.path.exists(f"{l}:\\")]
    return [os.path.expanduser("~")]


def buscar(consulta, raices, resultados, parar, n_hilos=HILOS):
    """
    Búsqueda multihilo sin límite de resultados.
    Cada carpeta con aciertos se envía en UNA sola llamada a 'resultados' (lista de rutas).
    Al terminar mete None en 'resultados'.
    """
    por_ruta = any(c in consulta for c in "/\\:")
    if por_ruta:
        consulta = consulta.replace("\\", "/")

    pendientes = queue.Queue()
    for r in raices:
        pendientes.put(r)

    def trabajador():
        obtener = pendientes.get
        meter = pendientes.put
        terminar = pendientes.task_done
        scandir = os.scandir
        enviar = resultados.put
        ignorar = IGNORAR
        incluir_carpetas = INCLUIR_CARPETAS
        while True:
            carpeta = obtener()
            if carpeta is None:
                return
            try:
                if not parar.is_set():
                    base = carpeta.replace("\\", "/").lower().rstrip("/") if por_ruta else ""
                    encontrados = []
                    agregar = encontrados.append
                    with scandir(carpeta) as it:
                        for e in it:
                            nombre = e.name.lower()
                            try:
                                if e.is_dir(follow_symlinks=False):
                                    if nombre not in ignorar:
                                        meter(e.path)
                                    if not incluir_carpetas:
                                        continue
                                if por_ruta:
                                    if consulta in f"{base}/{nombre}":
                                        agregar(e.path)
                                elif consulta in nombre:
                                    agregar(e.path)
                            except OSError:
                                pass
                    if encontrados:
                        enviar(encontrados)
            except OSError:
                pass
            finally:
                terminar()

    hilos = [threading.Thread(target=trabajador, daemon=True) for _ in range(n_hilos)]
    for h in hilos:
        h.start()
    pendientes.join()
    for _ in hilos:
        pendientes.put(None)
    resultados.put(None)


def abrir(ruta):
    try:
        if sys.platform.startswith("win"):
            os.startfile(ruta)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", ruta])
        else:
            subprocess.Popen(["xdg-open", ruta])
    except Exception as ex:
        messagebox.showerror("FileFinder", f"No se pudo abrir:\n{ex}")


def abrir_carpeta(ruta):
    try:
        if sys.platform.startswith("win"):
            subprocess.Popen(["explorer", "/select,", os.path.normpath(ruta)])
        else:
            abrir(os.path.dirname(ruta))
    except Exception as ex:
        messagebox.showerror("FileFinder", f"No se pudo abrir la carpeta:\n{ex}")


def _rect_redondeado(c, x1, y1, x2, y2, r, **kw):
    """Dibuja un rectángulo con esquinas redondeadas en un Canvas."""
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return c.create_polygon(pts, smooth=True, **kw)


class BotonRedondeado(tk.Canvas):
    """Botón plano con esquinas redondeadas y efecto hover."""

    def __init__(self, master, texto, comando, solido=True,
                 fuente=("Segoe UI", 10, "bold"), padx=20, pady=7):
        f = tkfont.Font(font=fuente)
        w = f.measure(texto) + 2 * padx
        h = f.metrics("linespace") + 2 * pady
        super().__init__(master, width=w, height=h, bg=BLANCO,
                         highlightthickness=0, bd=0)
        self._comando = comando
        self._solido = solido
        self._activo = True
        self._hover = False
        self._fondo = _rect_redondeado(self, 1, 1, w - 1, h - 1, 9, width=1)
        self._txt = self.create_text(w / 2, h / 2, text=texto, font=fuente)
        self._pintar()
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self.bind("<ButtonRelease-1>", self._soltar)

    def _set_hover(self, valor):
        self._hover = valor
        self._pintar()

    def _soltar(self, _e):
        if self._activo and self._hover:
            self._comando()

    def habilitar(self, activo):
        self._activo = activo
        self._pintar()

    def _pintar(self):
        if not self._activo:
            if self._solido:
                fondo, borde, fg = "#BBD7F5", "#BBD7F5", BLANCO
            else:
                fondo, borde, fg = BLANCO, GRIS_LINEA, "#B0B8C4"
        elif self._solido:
            fondo = borde = AZUL_OSCURO if self._hover else AZUL
            fg = BLANCO
        else:
            fondo = AZUL_CLARO if self._hover else BLANCO
            borde, fg = AZUL, AZUL
        self.itemconfig(self._fondo, fill=fondo, outline=borde)
        self.itemconfig(self._txt, fill=fg)
        self.configure(cursor="hand2" if self._activo else "arrow")


class CampoRedondeado(tk.Canvas):
    """Campo de texto con borde redondeado que se resalta en azul al enfocarlo."""

    def __init__(self, master, ancho=400, alto=40, fuente=("Segoe UI", 11)):
        super().__init__(master, width=ancho, height=alto, bg=BLANCO,
                         highlightthickness=0, bd=0)
        self._alto = alto
        self._foco = False
        self.entry = tk.Entry(self, font=fuente, relief="flat", bd=0, bg=BLANCO,
                              fg=GRIS_TEXTO, insertbackground=AZUL,
                              highlightthickness=0)
        self._win = self.create_window(14, alto / 2, window=self.entry, anchor="w")
        self.bind("<Configure>", self._dibujar)
        self.bind("<Button-1>", lambda e: self.entry.focus_set())
        self.entry.bind("<FocusIn>", lambda e: self._set_foco(True), add="+")
        self.entry.bind("<FocusOut>", lambda e: self._set_foco(False), add="+")

    def _set_foco(self, valor):
        self._foco = valor
        self._dibujar()

    def _dibujar(self, _e=None):
        w = self.winfo_width()
        if w < 10:
            return
        self.delete("fondo")
        _rect_redondeado(self, 2, 2, w - 2, self._alto - 2, 10, tags="fondo",
                         fill=BLANCO, outline=AZUL if self._foco else GRIS_BORDE,
                         width=2 if self._foco else 1)
        self.tag_lower("fondo")
        self.itemconfig(self._win, width=w - 28)


_estilos_scroll = set()


def crear_scrollbar(padre, orientacion, command=None):
    """Scrollbar fina y sin flechas; si el tema no lo permite, usa la estándar."""
    base = "Vertical" if orientacion == "vertical" else "Horizontal"
    nombre = f"Fino.{base}.TScrollbar"
    try:
        if nombre not in _estilos_scroll:
            estilo = ttk.Style(padre)
            estilo.theme_use("clam")
            estilo.layout(nombre, [(f"{base}.Scrollbar.trough", {
                "sticky": "ns" if base == "Vertical" else "ew",
                "children": [(f"{base}.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})],
            })])
            estilo.configure(nombre, background="#D3E1F2", troughcolor=BLANCO,
                             bordercolor=BLANCO, lightcolor="#D3E1F2", darkcolor="#D3E1F2",
                             relief="flat", width=10, arrowsize=10)
            estilo.map(nombre,
                       background=[("pressed", AZUL_OSCURO), ("active", AZUL)],
                       lightcolor=[("pressed", AZUL_OSCURO), ("active", AZUL)],
                       darkcolor=[("pressed", AZUL_OSCURO), ("active", AZUL)])
            _estilos_scroll.add(nombre)
        return ttk.Scrollbar(padre, orient=orientacion, style=nombre, command=command)
    except tk.TclError:
        return tk.Scrollbar(padre, orient=orientacion, command=command)


class ListaVirtual(tk.Frame):
    """
    Lista de resultados que solo dibuja las filas visibles.
    Los resultados son una lista Python normal: añadir miles de rutas o vaciarla
    es instantáneo y no depende de cuántos resultados haya.
    """

    def __init__(self, master, on_cambio=None, on_activar=None, on_menu=None):
        super().__init__(master, bg=BLANCO)
        self.items = []
        self.sel = None
        self.top = 0
        self.x = 0
        self.on_cambio = on_cambio
        self.on_activar = on_activar
        self.on_menu = on_menu

        self._fuente = tkfont.Font(font=("Segoe UI", 10))
        self._alto_fila = self._fuente.metrics("linespace") + 6
        self._ancho_max = 0
        self._pendiente = None
        self._textos = []

        self.canvas = tk.Canvas(self, bg=BLANCO, bd=0, highlightthickness=1,
                                highlightbackground=GRIS_LINEA,
                                highlightcolor=GRIS_LINEA, takefocus=1)
        self._sb_y = crear_scrollbar(self, "vertical", self._yview)
        self._sb_x = crear_scrollbar(self, "horizontal", self._xview)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self._sb_y.grid(row=0, column=1, sticky="ns")
        self._sb_x.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._sel_rect = self.canvas.create_rectangle(
            0, 0, 0, 0, fill=AZUL_SELECCION, outline="", state="hidden")

        c = self.canvas
        c.bind("<Configure>", lambda e: self.redibujar())
        c.bind("<Button-1>", self._clic)
        c.bind("<Double-Button-1>", self._doble)
        c.bind("<Button-3>", self._derecho)
        for tecla in ("<Up>", "<Down>", "<Prior>", "<Next>",
                      "<Home>", "<End>", "<Return>", "<KP_Enter>"):
            c.bind(tecla, self._tecla)
        c.bind("<Enter>", self._activar_rueda)
        c.bind("<Leave>", self._desactivar_rueda)

    def set_items(self, datos):
        self.items = list(datos)
        self.sel = None
        self.top = 0
        self.x = 0
        self._ancho_max = 0
        self.redibujar()
        self._avisar()

    def extender(self, datos):
        self.items.extend(datos)
        if self._pendiente is None:
            self._pendiente = self.after_idle(self._redibujo_diferido)

    def get_seleccion(self):
        if self.sel is not None and self.sel < len(self.items):
            return self.items[self.sel]
        return None

    def limpiar_seleccion(self):
        self.sel = None
        self.redibujar()
        self._avisar()

    def seleccionar(self, i, ver=True):
        self.sel = i
        if ver:
            visibles = self._filas_visibles()
            if i < self.top:
                self.top = i
            elif i >= self.top + visibles:
                self.top = i - visibles + 1
        self.redibujar()
        self._avisar()

    def _avisar(self):
        if self.on_cambio:
            self.on_cambio()

    def _filas_visibles(self):
        return max(1, self.canvas.winfo_height() // self._alto_fila)

    def _ancho_total(self):
        return max(self.canvas.winfo_width(), self._ancho_max + 24)

    def _redibujo_diferido(self):
        self._pendiente = None
        self.redibujar()

    def redibujar(self):
        c = self.canvas
        ancho, alto = c.winfo_width(), c.winfo_height()
        if ancho < 10 or alto < 10:
            return

        n = len(self.items)
        filas = max(1, alto // self._alto_fila)
        self.top = max(0, min(self.top, n - filas))

        primero = self.top
        ultimo = min(n, primero + filas + 1)
        visibles = self.items[primero:ultimo]

        medir = self._fuente.measure
        for t in visibles:
            w = medir(t)
            if w > self._ancho_max:
                self._ancho_max = w
        total_w = self._ancho_total()
        self.x = max(0, min(self.x, total_w - ancho))

        while len(self._textos) < filas + 1:
            self._textos.append(c.create_text(0, 0, anchor="w", font=self._fuente,
                                              fill=GRIS_TEXTO, state="hidden"))
        for k, tid in enumerate(self._textos):
            if k < len(visibles):
                i = primero + k
                c.itemconfigure(tid, text=visibles[k], state="normal",
                                fill=AZUL_TEXTO_SEL if i == self.sel else GRIS_TEXTO)
                c.coords(tid, 10 - self.x, k * self._alto_fila + self._alto_fila / 2)
            else:
                c.itemconfigure(tid, state="hidden")

        if self.sel is not None and primero <= self.sel < ultimo:
            y0 = (self.sel - primero) * self._alto_fila
            c.coords(self._sel_rect, 0, y0, ancho, y0 + self._alto_fila)
            c.itemconfigure(self._sel_rect, state="normal")
        else:
            c.itemconfigure(self._sel_rect, state="hidden")
        c.tag_lower(self._sel_rect)

        if n:
            self._sb_y.set(primero / n, min(n, primero + filas) / n)
        else:
            self._sb_y.set(0, 1)
        self._sb_x.set(self.x / total_w, min(1, (self.x + ancho) / total_w))

    def _yview(self, accion, valor, unidad=None):
        n = len(self.items)
        if accion == "moveto":
            self.top = int(float(valor) * n)
        else:
            paso = max(1, self._filas_visibles() - 1) if unidad == "pages" else 3
            self.top += int(valor) * paso
        self.redibujar()

    def _xview(self, accion, valor, unidad=None):
        if accion == "moveto":
            self.x = int(float(valor) * self._ancho_total())
        else:
            paso = max(20, self.canvas.winfo_width() - 40) if unidad == "pages" else 30
            self.x += int(valor) * paso
        self.redibujar()

    def _rueda(self, e):
        if e.num == 4:
            sentido = -1
        elif e.num == 5:
            sentido = 1
        else:
            sentido = -1 if e.delta > 0 else 1
        if e.state & 0x0001:
            self.x += sentido * 40
        else:
            self.top += sentido * 3
        self.redibujar()

    def _activar_rueda(self, _e=None):
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.bind_all(seq, self._rueda)

    def _desactivar_rueda(self, _e=None):
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.unbind_all(seq)

    def _indice_en(self, y):
        i = self.top + y // self._alto_fila
        return i if 0 <= i < len(self.items) else None

    def _clic(self, e):
        self.canvas.focus_set()
        i = self._indice_en(e.y)
        if i is not None:
            self.seleccionar(i, ver=False)

    def _doble(self, e):
        i = self._indice_en(e.y)
        if i is not None:
            self.seleccionar(i, ver=False)
            if self.on_activar:
                self.on_activar()

    def _derecho(self, e):
        i = self._indice_en(e.y)
        if i is not None:
            self.seleccionar(i, ver=False)
            if self.on_menu:
                self.on_menu(e)

    def _tecla(self, e):
        n = len(self.items)
        if not n:
            return
        if e.keysym in ("Return", "KP_Enter"):
            if self.sel is not None and self.on_activar:
                self.on_activar()
            return
        pagina = max(1, self._filas_visibles() - 1)
        actual = -1 if self.sel is None else self.sel
        destino = {
            "Up": actual - 1, "Down": actual + 1,
            "Prior": actual - pagina, "Next": actual + pagina,
            "Home": 0, "End": n - 1,
        }.get(e.keysym)
        if destino is not None:
            self.seleccionar(min(max(destino, 0), n - 1))


class FileFinder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FileFinder")
        self.configure(bg=BLANCO)
        try:
            self._icono = tk.PhotoImage(data=PATO_ICONO)
            self.iconphoto(True, self._icono)
        except tk.TclError:
            pass
        self._centrar()
        self.resizable(False, False)

        self.cola = queue.Queue()
        self.parar = threading.Event()
        self.id_busqueda = 0
        self.total = 0
        self.modo_historial = False
        self.historial = self._cargar_historial()

        self.espacio_superior = tk.Frame(self, bg=BLANCO, height=0)
        self.espacio_superior.pack()

        self.cabecera = tk.Frame(self, bg=BLANCO)
        self.cabecera.pack(pady=(0, 8))
        self.logo = tk.Frame(self.cabecera, bg=BLANCO, cursor="hand2")
        self.logo_file = tk.Label(self.logo, text="File", font=("Segoe UI", 26, "bold"),
                                  fg=AZUL, bg=BLANCO, cursor="hand2")
        self.logo_file.pack(side="left")
        self.logo_finder = tk.Label(self.logo, text="Finder.", font=("Segoe UI", 26, "bold"),
                                    fg=GRIS_TEXTO, bg=BLANCO, cursor="hand2")
        self.logo_finder.pack(side="left")
        self.logo.pack(side="left")
        self.pato = tk.Label(self.cabecera, bg=BLANCO, cursor="hand2", bd=0)
        self.pato.pack(side="left", padx=(12, 0))
        for parte_logo in (self.logo, self.logo_file, self.logo_finder):
            parte_logo.bind("<Button-1>", self._volver_inicio)
        self.pato.bind("<Button-1>", self._volver_inicio)
        self._cargar_pato()

        self.campo = CampoRedondeado(self, ancho=min(int(self.ancho_ventana * ANCHO_CAJA), 520))
        self.campo.pack(pady=(4, 12))
        self.entrada = self.campo.entry
        self.placeholder = "Introduce el nombre del archivo que buscas"
        self.placeholder_visible = True
        self.entrada.insert(0, self.placeholder)
        self.entrada.config(fg="#9AA5B1")
        self.entrada.bind("<FocusIn>", self._quitar_placeholder, add="+")
        self.entrada.bind("<FocusOut>", self._poner_placeholder, add="+")
        self.entrada.bind("<KeyPress>", self._quitar_placeholder, add="+")
        self.entrada.bind("<Return>", lambda e: self.iniciar_busqueda())

        self.marco_botones = tk.Frame(self, bg=BLANCO)
        self.marco_botones.pack(pady=(0, 12))
        BotonRedondeado(self.marco_botones, "Buscar", self.iniciar_busqueda,
                        solido=True, padx=30).pack(side="left", padx=(0, 8))
        BotonRedondeado(self.marco_botones, "Historial de búsquedas",
                        self.mostrar_historial, solido=False,
                        padx=18).pack(side="left")

        self.panel_resultados = tk.Frame(self, bg=BLANCO)
        tk.Frame(self.panel_resultados, height=1, bg=GRIS_LINEA).pack(fill="x", padx=26)

        self.estado = tk.Label(self.panel_resultados, text="", font=("Segoe UI", 9),
                               fg=GRIS_SUAVE, bg=BLANCO, anchor="w")
        self.estado.pack(fill="x", padx=26, pady=(8, 5))

        barra = tk.Frame(self.panel_resultados, bg=BLANCO)
        barra.pack(side="bottom", fill="x", padx=26, pady=(4, 16))
        self.botones_accion = []
        for texto, comando in (
            ("Abrir archivo", self._abrir_seleccion),
            ("Abrir carpeta contenedora", self._abrir_carpeta_sel),
            ("Copiar ruta", self._copiar_ruta),
        ):
            b = BotonRedondeado(barra, texto, comando, solido=False,
                                fuente=("Segoe UI", 9), padx=12, pady=5)
            b.pack(side="left", padx=(0, 6))
            b.habilitar(False)
            self.botones_accion.append(b)

        self.lista = ListaVirtual(self.panel_resultados,
                                  on_cambio=self._al_cambiar,
                                  on_activar=self._al_activar,
                                  on_menu=self._mostrar_menu)
        self.lista.pack(fill="both", expand=True, padx=26, pady=(0, 4))

        tk.Label(self, text=VERSION, font=("Segoe UI", 8), fg=GRIS_SUAVE,
                 bg=BLANCO, bd=0).place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-6)

        self.bind("<Escape>", self._deseleccionar)

        self.menu = tk.Menu(self, tearoff=0, bg=BLANCO, fg=GRIS_TEXTO,
                            activebackground=AZUL, activeforeground=BLANCO,
                            relief="flat", bd=1)
        self.menu.add_command(label="Abrir archivo", command=self._abrir_seleccion)
        self.menu.add_command(label="Abrir carpeta contenedora", command=self._abrir_carpeta_sel)
        self.menu.add_command(label="Copiar ruta", command=self._copiar_ruta)

        self._modo_inicio(True)

    def _centrar(self):
        pw, ph = self.winfo_screenwidth(), self.winfo_screenheight()
        factor = PORCENTAJE_PANTALLA ** 0.5
        w = max(int(pw * factor), 520)
        h = max(int(ph * factor), 460)
        x, y = (pw - w) // 2, (ph - h) // 2
        self.ancho_ventana, self.alto_ventana = w, h
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _cargar_pato(self):
        """Carga cada fotograma del pato y lo escala al tamaño del texto del título.
        Si un fotograma no se puede decodificar, se omite y se avisa por consola
        en lugar de desactivar el pato entero."""
        self.frames_pato = []
        originales = []
        for i, datos in enumerate(PATO_FRAMES):
            try:
                originales.append(tk.PhotoImage(data=datos))
            except tk.TclError as ex:
                print(f"FileFinder: fotograma {i} del pato no válido: {ex}", file=sys.stderr)

        if not originales:
            self.pato.pack_forget()
            return

        try:
            objetivo = self.winfo_fpixels("26p") * 1.15
            alto = originales[0].height()
            a, b = min(((a, b) for b in (1, 2) for a in range(1, 25)),
                       key=lambda ab: (abs(ab[0] / ab[1] * alto - objetivo), ab[1]))
            for f in originales:
                f = f.zoom(a) if a > 1 else f
                self.frames_pato.append(f.subsample(b) if b > 1 else f)
        except tk.TclError:
            self.frames_pato = originales

        self.pato.config(image=self.frames_pato[0])
        self._animar_pato()

    def _animar_pato(self, i=0):
        self.pato.config(image=self.frames_pato[i])
        self.after(VELOCIDAD_PATO, self._animar_pato, (i + 1) % len(self.frames_pato))

    def _modo_inicio(self, inicio):
        """Inicio: logo y caja centrados verticalmente. Con resultados: arriba."""
        if inicio:
            self.update_idletasks()
            contenido = (self.cabecera.winfo_reqheight() + 8 +
                         self.campo.winfo_reqheight() + 16 +
                         self.marco_botones.winfo_reqheight() + 12)
            altura = max(0, (self.alto_ventana - contenido) // 2 - 16)
        else:
            altura = 14
        self.espacio_superior.config(height=max(altura, 1))

    def _mostrar_vista_resultados(self):
        if not self.panel_resultados.winfo_manager():
            self._modo_inicio(False)
            self.panel_resultados.pack(fill="both", expand=True)

    def _quitar_placeholder(self, _event=None):
        if self.placeholder_visible:
            self.entrada.delete(0, "end")
            self.entrada.config(fg=GRIS_TEXTO)
            self.placeholder_visible = False

    def _poner_placeholder(self, _event=None):
        if not self.entrada.get():
            self.entrada.insert(0, self.placeholder)
            self.entrada.config(fg="#9AA5B1")
            self.placeholder_visible = True

    def _cancelar_busqueda(self):
        self.parar.set()
        self.id_busqueda += 1

    def _volver_inicio(self, _event=None):
        self._cancelar_busqueda()
        self.modo_historial = False
        self.lista.set_items([])
        self.panel_resultados.pack_forget()
        self._modo_inicio(True)
        self.entrada.delete(0, "end")
        self.placeholder_visible = False
        self._poner_placeholder()
        self.estado.config(text="")
        self.total = 0

    def iniciar_busqueda(self):
        if self.placeholder_visible:
            self._mensaje("Escribe algo para buscar.")
            return
        texto = self.entrada.get()
        texto = (texto if texto and not texto.strip() else texto.strip()).lower()
        if not texto:
            self._mensaje("Escribe algo para buscar.")
            return
        prohibidos = [c for c in SIMBOLOS_PROHIBIDOS if c in texto]
        if prohibidos:
            self._mensaje(f"Windows no permite {' '.join(prohibidos)} en nombres de archivo, "
                          "así que no puede haber coincidencias.")
            return
        self._buscar_texto(texto)

    def _mensaje(self, texto):
        self._mostrar_vista_resultados()
        self._cancelar_busqueda()
        self.modo_historial = False
        self.lista.set_items([])
        self.estado.config(text=texto)

    def _buscar_texto(self, texto):
        self._mostrar_vista_resultados()
        self.entrada.delete(0, "end")
        self.entrada.insert(0, texto)
        self.entrada.config(fg=GRIS_TEXTO)
        self.placeholder_visible = False
        self._agregar_al_historial(texto)
        self.modo_historial = False

        self._cancelar_busqueda()
        mi_id = self.id_busqueda
        self.parar = threading.Event()
        self.cola = queue.Queue()
        self.total = 0
        self.lista.set_items([])
        self.estado.config(text="Buscando...")

        threading.Thread(target=buscar,
                         args=(texto, obtener_raices(), self.cola, self.parar),
                         daemon=True).start()
        self.after(20, self._leer_cola, mi_id, self.cola)

    def _leer_cola(self, mi_id, cola):
        if mi_id != self.id_busqueda:
            return
        terminado = False
        limite = time.perf_counter() + TIEMPO_UI
        while time.perf_counter() < limite:
            try:
                item = cola.get_nowait()
            except queue.Empty:
                break
            if item is None:
                terminado = True
                break
            self.lista.extender(item)
            self.total += len(item)

        if terminado:
            self.estado.config(
                text=f"{formato_numero(self.total)} resultado{'s' if self.total != 1 else ''}")
        else:
            self.estado.config(text=f"Buscando... {formato_numero(self.total)} encontrados")
            self.after(30, self._leer_cola, mi_id, cola)

    def mostrar_historial(self):
        self._mostrar_vista_resultados()
        self._cancelar_busqueda()
        self.modo_historial = True
        self.lista.set_items(self.historial)
        if self.historial:
            n = len(self.historial)
            self.estado.config(text=f"{n} búsqueda{'s' if n != 1 else ''} en el historial")
        else:
            self.estado.config(text="Todavía no hay búsquedas en el historial.")

    def _cargar_historial(self):
        archivo = ruta_historial()
        try:
            with open(archivo, "r", encoding="utf-8") as historial_file:
                historial = json.load(historial_file)
            if not isinstance(historial, list) or not all(
                isinstance(termino, str) for termino in historial
            ):
                raise ValueError("El formato del historial no es válido.")
            return historial
        except FileNotFoundError:
            return []
        except (OSError, json.JSONDecodeError, ValueError) as ex:
            messagebox.showerror(
                "FileFinder", f"No se pudo cargar el historial:\n{ex}"
            )
            return []

    def _agregar_al_historial(self, termino):
        if not termino.strip():
            return
        self.historial = [termino] + [
            anterior for anterior in self.historial if anterior != termino
        ]
        archivo = ruta_historial()
        temporal = archivo + ".tmp"
        try:
            os.makedirs(os.path.dirname(archivo), exist_ok=True)
            with open(temporal, "w", encoding="utf-8") as historial_file:
                json.dump(self.historial, historial_file, ensure_ascii=False, indent=2)
            os.replace(temporal, archivo)
        except OSError as ex:
            messagebox.showerror(
                "FileFinder", f"No se pudo guardar el historial:\n{ex}"
            )

    def _actualizar_botones(self, activo):
        for b in self.botones_accion:
            b.habilitar(activo)

    def _al_cambiar(self):
        self._actualizar_botones(not self.modo_historial and self.lista.sel is not None)

    def _al_activar(self):
        """Doble clic o Enter: en el historial busca el término; en resultados abre el archivo."""
        if self.modo_historial:
            termino = self.lista.get_seleccion()
            if termino:
                self._buscar_texto(termino)
        else:
            self._abrir_seleccion()

    def _deseleccionar(self, _event=None):
        self.lista.limpiar_seleccion()

    def _seleccion(self):
        return None if self.modo_historial else self.lista.get_seleccion()

    def _abrir_seleccion(self, _event=None):
        ruta = self._seleccion()
        if ruta:
            abrir(ruta)

    def _abrir_carpeta_sel(self):
        ruta = self._seleccion()
        if ruta:
            abrir_carpeta(ruta)

    def _copiar_ruta(self):
        ruta = self._seleccion()
        if ruta:
            self.clipboard_clear()
            self.clipboard_append(ruta)

    def _mostrar_menu(self, event):
        if self.modo_historial or not self.lista.items:
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