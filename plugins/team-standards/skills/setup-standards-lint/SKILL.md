---
name: setup-standards-lint
description: Instala en el repositorio actual los chequeos mecánicos del estándar del equipo (largo máximo de archivo, comentarios en inglés) como hooks de pre-commit. Úsala cuando el usuario pida instalar/configurar los chequeos del estándar, los hooks de pre-commit del equipo, o "aplica el estándar a este repo", "instala los pre-commit del equipo", "configura los chequeos de estándar aquí", "quiero que este repo valide largo de archivos", "setup de lint del equipo". También aplica si pregunta por qué un chequeo no está corriendo en un repo.
allowed-tools: Read, Write, Edit, Bash, Glob
---

# Instalar los chequeos mecánicos del estándar

Instala en **el repositorio en el que estás ahora** (no en el marketplace) los verificadores
que empaqueta este plugin, como hooks de `pre-commit`.

La propiedad crítica del diseño: **los hooks revisan solo los archivos que el commit toca.**
El código preexistente que no cumple no bloquea nada hasta que alguien lo edita. No intentes
"arreglar todo el repo" desde esta skill.

## Reglas importantes

- **Nunca sobrescribas un `.pre-commit-config.yaml` existente.** Si ya hay uno, agrega
  únicamente los hooks que falten, preservando todo lo demás tal como está.
- **No corras `pre-commit run --all-files` como parte de la instalación.** Sobre un repo con
  historia va a fallar masivamente por deuda previa, que es exactamente lo que este diseño
  evita bloquear. Si el usuario quiere ese panorama, la skill `standards-audit` (plugin
  `dev-toolkit`) lo entrega como informe, sin bloquear commits.
- Si el repo no usa `pre-commit`, explícalo y pide confirmación antes de introducirlo: es una
  dependencia de desarrollo nueva para ese proyecto.

## Paso 1 — Confirmar dónde estás

Verifica que estás en un repositorio de trabajo y no en el marketplace:

```bash
git rev-parse --show-toplevel
ls .claude-plugin 2>/dev/null && echo "OJO: esto parece el marketplace"
```

Si aparece `.claude-plugin/marketplace.json`, detente: esta skill se corre en los repos de
producto, no en el marketplace.

## Paso 2 — Detectar el stack

Mira qué hay en la raíz para saber qué hooks tienen sentido:

- `pyproject.toml` / `requirements*.txt` / `setup.py` → Python.
- `package.json` → JS/TS (revisa si ya hay `eslint` y `prettier` configurados).
- Ambos → monorepo o proyecto mixto; instala los dos.

Revisa también si ya existe `.pre-commit-config.yaml` y si `pre-commit` está disponible
(`pre-commit --version`).

## Paso 3 — Copiar los verificadores

Copia los scripts a `.standards/` en la raíz del repo y hazlos ejecutables:

```bash
mkdir -p .standards
cp ${CLAUDE_PLUGIN_ROOT}/pre-commit/check_file_length.py .standards/
cp ${CLAUDE_PLUGIN_ROOT}/pre-commit/check_comment_language.py .standards/
chmod +x .standards/*.py
```

Se copian (en vez de referenciarse desde el plugin) a propósito: así el repo sigue validando
en CI y en las máquinas de quienes no tengan el plugin instalado.

## Paso 4 — Configurar `.pre-commit-config.yaml`

La plantilla de referencia está en
`${CLAUDE_PLUGIN_ROOT}/pre-commit/pre-commit-config.template.yaml`. Léela y luego:

- **Si no existe** `.pre-commit-config.yaml`: créalo a partir de la plantilla, dejando
  activos solo los hooks que apliquen al stack detectado.
- **Si ya existe**: léelo completo y agrega únicamente los hooks `imfd-file-length` e
  `imfd-comment-language` que falten, respetando el formato y el orden existentes. No toques
  los hooks que ya estaban, ni cambies sus `rev` ni sus argumentos.

Si el repo ya tiene `black`, `eslint` o `prettier` configurados de otra forma, **déjalos como
están** — el estándar pide que existan, no que se declaren de una manera específica.

## Paso 5 — Activar los hooks

```bash
pre-commit install
```

Si `pre-commit` no está instalado, indícale al usuario cómo agregarlo como dependencia de
desarrollo del proyecto (según su gestor: `pip`, `uv`, `poetry`), sin instalarlo globalmente
por tu cuenta.

## Paso 6 — Verificar que funciona, sin tocar el repo

Prueba los hooks contra un archivo cualquiera del repo para confirmar que corren:

```bash
pre-commit run imfd-file-length --files <un-archivo-existente>
```

Si un archivo legacy falla, eso es **esperado y correcto**: solo importará cuando alguien
edite ese archivo. Explícaselo al usuario en vez de corregirlo aquí.

## Paso 7 — Reportar

Cierra con un resumen corto:

- Qué se creó o modificó (`.standards/`, `.pre-commit-config.yaml`).
- Qué hooks quedaron activos y sobre qué extensiones.
- Si `pre-commit install` quedó pendiente de que el usuario instale la herramienta.
- Recuérdale que los umbrales (300/400 líneas) se ajustan por repo en el
  `.pre-commit-config.yaml` con un comentario que explique por qué, y que silenciar un
  chequeo inline también requiere comentario justificando.
- Si el repo arrastra mucha deuda, menciona `standards-audit` como la vía para verla completa.
