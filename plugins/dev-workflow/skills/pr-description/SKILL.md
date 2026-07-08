---
name: pr-description
description: "Genera el markdown para la descripcion de una Pull Request de GitHub, comparando la rama actual con una rama destino (main por defecto). Usa esta skill siempre que el usuario pida generar/armar/redactar la descripcion o el markdown de un PR o MR, pida comparar la rama actual con main (o con otra rama) para preparar un pull request, o pida un resumen de cambios para subir a GitHub. Tambien aplica si menciona 'PR', 'pull request', 'MR', 'merge request', o pide copiar la descripcion del PR al portapapeles."
---

# Generador de descripción de PR

Genera el markdown de la descripción de un Pull Request analizando el diff
de la rama actual contra una rama destino, siguiendo siempre la misma
plantilla y dejando claramente marcado todo lo que el usuario deba
completar a mano.

## Plantilla de referencia

Secciones y orden fijo (encabezados `##`):

1. **Context** — por qué se hacen estos cambios.
2. **Changelog** — qué cambios se hicieron.
3. **How to test** — pasos para probar/reproducir.
4. **Screenshots (Optional)** — solo si hay cambios de frontend/vista.
5. **Notes (Optional)** — solo si hay algo relevante que anotar (breaking
   changes, deuda técnica, issues conocidos).

Estilo del Changelog (ver `references/example.md` para el caso completo):
cada ítem en negrita con un nombre corto del cambio, seguido del tag
`tipo(contexto)` entre backticks (tomado del mensaje de commit si sigue esa
convención), y luego la descripción en prosa.

```
* **DB schema cleanup** (`refactor(db-model)`): descripción del cambio...
```

## Flujo de trabajo

### 1. Determinar rama destino

- Por defecto es `main`.
- Si el usuario indica otra rama ("hacia develop", "target: staging", "esta
  va contra release/2.0"), usar esa en vez de `main`.
- Nunca asumas en silencio una rama distinta a `main` sin que el usuario lo
  haya pedido.

### 2. Recolectar los cambios

Ejecuta el script bundleado, pasando la rama destino solo si el usuario la
especificó:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/gather_changes.sh [rama-destino]
```

Esto entrega: rama actual, rama destino resuelta, lista de commits
(`merge-base..HEAD`), diff stat, archivos modificados y el diff completo
(comparado siempre desde el merge-base con `...`, nunca un diff lineal, para
no arrastrar cambios ya integrados en destino).

Si el script falla (rama destino inexistente, mismo branch, detached HEAD),
muestra el error al usuario y pide la aclaración necesaria antes de seguir.

### 3. Analizar los cambios

- **Si los commits siguen la convención `tipo(contexto): descripción`**
  (ver skill `git-commits`), úsalos como base directa del Changelog: cada
  commit (o grupo de commits relacionados) se convierte en un ítem con su
  tag `tipo(contexto)`.
- **Si no siguen esa convención**, agrupa los cambios del diff por
  módulo/carpeta afectada e infiere un tipo razonable (feat/fix/refactor/etc.)
  solo como etiqueta descriptiva, sin inventar un mensaje de commit que no
  existe.
- Identifica si hay archivos de frontend/vista modificados (`.tsx`, `.jsx`,
  `.vue`, `.svelte`, `.css`, `.scss`, `.html`, componentes de UI) — esto
  determina si va la sección Screenshots.
- Identifica cambios que ameriten una nota para el reviewer: breaking
  changes, renombres de variables de entorno, migraciones de base de datos,
  deuda técnica conocida, TODOs dejados a propósito.

### 4. Redactar cada sección

- **Context**: 1–3 frases explicando el porqué. Si no es inferible del
  diff/commits/conversación, no lo inventes — déjalo marcado (ver más abajo).
- **Changelog**: lista de bullets en el formato de la plantilla.
- **How to test**: pasos concretos y numerados. Si un paso requiere algo que
  no puedes saber (credenciales, otra rama de otro repo, variables de
  entorno específicas de un ambiente, orden exacto de verificación manual),
  no lo inventes — márcalo.
- **Screenshots (Optional)**: inclúyela SOLO si detectaste cambios de
  frontend. Si se incluye, siempre queda marcada como pendiente (las
  capturas las adjunta el usuario). Si no aplica, omite la sección completa
  (no la dejes vacía).
- **Notes (Optional)**: inclúyela solo si hay algo que valga la pena anotar.
  Si no aplica, omite la sección completa.

### 5. Marcar lo pendiente de forma imposible de pasar por alto

Cualquier parte que el usuario deba completar, revisar o adjuntar
manualmente (contexto no inferible, pasos de testing que no puedes conocer,
capturas de pantalla) se marca siempre con este bloque, justo debajo de la
línea o ítem afectado:

```
> ⚠️ **COMPLETAR:** <qué falta y por qué no se pudo inferir>
```

Nunca rellenes esos huecos con contenido inventado o genérico solo para que
la sección "se vea completa".

### 6. Ensamblar el markdown final

Usa exactamente este esqueleto (omitiendo Screenshots/Notes si no aplican):

```markdown
## Context

<contenido o bloque de COMPLETAR>

## Changelog

* **<nombre>** (`<tipo(contexto)>`): <descripción>
* ...

## How to test

1. <paso>
2. ...

## Screenshots (Optional)

> ⚠️ **COMPLETAR:** adjuntar capturas de los cambios de frontend antes de publicar el PR

## Notes (Optional)

<notas relevantes>
```

### 7. Copiar al portapapeles

Guarda el markdown final en un archivo temporal y cópialo con:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/copy_to_clipboard.sh <archivo-temporal>
```

- Si el script confirma éxito (`OK: ...`), avisa brevemente al usuario cómo
  se copió (ej. "copiado con xclip").
- Si falla (`WARN: ...`), dile explícitamente al usuario que no se pudo
  copiar automáticamente y por qué (herramienta faltante), pero igual
  muéstrale el markdown completo para que lo copie manualmente.

### 8. Mostrar el resultado

Muestra siempre el markdown completo en un bloque de código en tu
respuesta, aunque se haya copiado exitosamente al portapapeles — así el
usuario puede previsualizarlo y ver de inmediato los bloques `⚠️ COMPLETAR`
antes de pegarlo en GitHub.

## Reglas duras

- Nunca inventes contenido específico (contexto, pasos de testing,
  credenciales, links a otros repos) que no se pueda inferir del diff, los
  commits, o la conversación — todo eso va marcado con `⚠️ COMPLETAR`.
- Siempre compara contra el merge-base (`...`), nunca un diff lineal simple.
- Siempre respeta el orden de secciones de la plantilla.
- Screenshots solo aparece si hay cambios de frontend; Notes solo si hay
  algo que valga la pena anotar. Nunca dejes una sección opcional vacía.
- Siempre intenta copiar al portapapeles y siempre muestra el markdown en la
  respuesta, sin importar si la copia tuvo éxito o no.
- La rama destino por defecto es `main`; solo cambia si el usuario lo pide.

## Referencia

Ver `references/example.md` para un ejemplo completo de un PR real con el
nivel de detalle esperado para cambios grandes (para cambios chicos, el
resultado puede ser bastante más breve).
