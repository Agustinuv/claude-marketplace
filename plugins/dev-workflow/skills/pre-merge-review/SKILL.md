---
name: pre-merge-review
description: Revisa exhaustivamente los cambios de una rama que aún no están en main/master, antes de integrarla. Evalúa funcionalidad, casos borde, optimizaciones, seguridad, buenas prácticas y tests, y entrega un veredicto (visto bueno o plan de mejora). Úsala SIEMPRE que el usuario pida revisar una rama, hacer code review, evaluar cambios antes de un merge o pull request, decidir si algo está listo para main, o pida un visto bueno / go-no-go sobre código. Frases típicas que la disparan: "revisa esta rama", "¿está lista para main?", "evalúa los cambios antes de mergear", "hazme un code review", "review del PR", "¿puedo mergear esto?", "revisa lo que cambié en esta branch".
---

# Pre-Merge Review

Revisión rigurosa de una rama de trabajo **antes** de integrarla a la rama base (normalmente `main`).
El objetivo es darle al usuario una de dos cosas: un **visto bueno claro para mergear**, o un
**plan de mejora accionable** con los problemas ordenados por severidad.

## Reglas importantes

- **No modifiques código.** Esta skill solo analiza y produce un informe. No edites archivos,
  no hagas commits, no ejecutes el merge. Si el usuario quiere que apliques arreglos, eso es un
  paso posterior y explícito.
- **Fundamenta cada hallazgo en el diff real**, no en suposiciones. Si necesitas más contexto del
  que muestra el diff, abre el archivo completo correspondiente antes de opinar.
- **Sé concreto.** Cada hallazgo debe apuntar a un archivo y, cuando se pueda, a una línea o función.

## Paso 1 — Establecer el contexto

Determina la rama actual y la rama base, y trae lo último del remoto sin tocar el working tree:

```bash
# Trae referencias actualizadas (no modifica tu árbol de trabajo)
git fetch --quiet origin 2>/dev/null || true

# Rama actual
git rev-parse --abbrev-ref HEAD

# Rama base por defecto del remoto (main, master, develop...). Si falla, asume main y luego master.
git symbolic-ref --quiet refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'
```

Elige como base `origin/<rama-base>` si existe; si no, usa la rama local (`main`/`master`).
Si el usuario indica otra base (ej. `develop`), respétala.

## Paso 2 — Recolectar los cambios

Usa el operador de tres puntos (`base...HEAD`): muestra exactamente lo que la rama introdujo
desde que se separó de la base, sin mezclar cambios que ocurrieron en la base mientras tanto.

```bash
BASE=origin/main   # ajusta según lo detectado en el Paso 1

# Resumen de archivos tocados
git diff --stat "$BASE"...HEAD

# Historial de commits de la rama
git log "$BASE"..HEAD --oneline

# El diff completo (la fuente principal de la revisión)
git diff "$BASE"...HEAD
```

Si hay cambios sin commitear que también deban evaluarse, revísalos aparte con
`git status` y `git diff` (working tree) y acláralo en el informe.

Para archivos con cambios densos o lógica compleja, **lee el archivo completo** (no solo el hunk del
diff) para entender el contexto antes de juzgar.

## Paso 3 — Analizar

Recorre los cambios cubriendo estas dimensiones. No todas aplican a cada rama; omite las que no vengan al caso.

- **Funcionalidad y corrección**: ¿el código hace lo que dice el commit/PR? ¿hay bugs lógicos?
- **Casos borde y manejo de errores**: nulos/vacíos, límites, concurrencia, fallos de red/IO,
  inputs inesperados, estados intermedios.
- **Optimizaciones**: complejidad innecesaria, queries N+1, falta de índices, llamados repetidos,
  cargas en memoria evitables, falta de paginación o batching.
- **Buenas prácticas y legibilidad**: nombres claros, funciones cohesionadas, duplicación,
  consistencia con las convenciones del resto del repo, comentarios donde aporten.
- **Seguridad**: validación de inputs, secretos hardcodeados, inyección (SQL/command),
  permisos/authz, exposición de datos sensibles en logs o respuestas.
- **Tests**: ¿lo nuevo está cubierto? ¿los tests prueban el comportamiento, no solo la implementación?
  ¿faltan casos borde en los tests?
- **Consistencia**: encaja con la arquitectura y los patrones ya presentes en el proyecto.

Asigna a cada hallazgo una severidad:

- **Bloqueante** — debe arreglarse antes de mergear (bug, riesgo de seguridad, regresión).
- **Importante** — debería arreglarse, pero no necesariamente bloquea (deuda real, riesgo medio).
- **Menor / sugerencia** — mejora opcional (estilo, micro-optimización, nit).

## Paso 4 — Veredicto y entregable

Decide el veredicto según la severidad más alta encontrada:

- ✅ **Aprobado** — sin bloqueantes ni importantes; listo para mergear.
- ⚠️ **Aprobado con observaciones** — sin bloqueantes, pero hay importantes a considerar.
- ❌ **Requiere cambios** — hay al menos un bloqueante; no mergear aún.

## Plantilla de salida

Usa SIEMPRE esta estructura:

```markdown
# Revisión pre-merge: `<rama-actual>` → `<rama-base>`

**Veredicto:** <✅ Aprobado | ⚠️ Aprobado con observaciones | ❌ Requiere cambios>

## Resumen
<2-4 frases: qué hace la rama, alcance del cambio, impresión general.>

## Alcance
- Commits: <n>
- Archivos modificados: <n> (+<adds> / -<dels>)

## Hallazgos

### 🔴 Bloqueantes
- **`ruta/archivo.py:123`** — <descripción del problema y por qué bloquea> · *Sugerencia:* <cómo resolverlo>

### 🟠 Importantes
- **`ruta/archivo.ts`** — <descripción> · *Sugerencia:* <...>

### 🟡 Menores / sugerencias
- **`ruta/archivo`** — <descripción>

(Omite las secciones que queden vacías.)

## Plan de mejora
1. <acción concreta y ordenada por prioridad>
2. <...>

## Qué está bien
<1-3 puntos de lo que se hizo bien, para dar contexto balanceado.>
```

Si el veredicto es ✅ y no hay hallazgos, igual incluye el resumen, el alcance y "Qué está bien",
y reemplaza las secciones de hallazgos por una línea: "Sin observaciones. Listo para merge."

## Ejemplo de un hallazgo bien escrito

Mal (vago):
> Hay un problema de rendimiento en el servicio.

Bien (accionable):
> **`services/sync.py:88`** — Se hace un `SELECT` por cada elemento del loop (N+1) al sincronizar
> con PostgreSQL; con lotes grandes esto degrada el tiempo de sync linealmente. *Sugerencia:*
> reemplazar por un `INSERT` multi-fila batcheado, como ya se hace en `services/seed.py`.
