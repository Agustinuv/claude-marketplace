#!/usr/bin/env bash
# Copia el contenido de un archivo al portapapeles, probando distintas
# herramientas según el sistema operativo disponible.
#
# Uso: copy_to_clipboard.sh <archivo>

set -uo pipefail

FILE="${1:-}"

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "ERROR: debes indicar un archivo válido a copiar." >&2
  exit 1
fi

if command -v pbcopy >/dev/null 2>&1; then
  pbcopy < "$FILE"
  echo "OK: copiado al portapapeles con pbcopy (macOS)"
  exit 0
fi

if command -v wl-copy >/dev/null 2>&1; then
  wl-copy < "$FILE"
  echo "OK: copiado al portapapeles con wl-copy (Wayland)"
  exit 0
fi

if command -v xclip >/dev/null 2>&1; then
  xclip -selection clipboard < "$FILE"
  echo "OK: copiado al portapapeles con xclip (X11)"
  exit 0
fi

if command -v xsel >/dev/null 2>&1; then
  xsel --clipboard --input < "$FILE"
  echo "OK: copiado al portapapeles con xsel (X11)"
  exit 0
fi

if command -v clip.exe >/dev/null 2>&1; then
  clip.exe < "$FILE"
  echo "OK: copiado al portapapeles con clip.exe (WSL/Windows)"
  exit 0
fi

if command -v powershell.exe >/dev/null 2>&1; then
  powershell.exe -NoProfile -Command "Get-Content -Raw -LiteralPath '$FILE' | Set-Clipboard"
  echo "OK: copiado al portapapeles con PowerShell Set-Clipboard"
  exit 0
fi

echo "WARN: no se encontró ninguna herramienta de portapapeles (pbcopy/wl-copy/xclip/xsel/clip.exe/powershell.exe)." >&2
echo "WARN: instala 'xclip' o 'xsel' (Linux) para habilitar el copiado automático." >&2
exit 1
