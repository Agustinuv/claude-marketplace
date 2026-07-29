---
name: standards-audit
description: Audita código existente contra el estándar del equipo y entrega un informe priorizado por módulo, sin modificar nada. Úsala cuando el usuario quiera saber cuánta deuda arrastra un repo o un módulo respecto de las convenciones: archivos demasiado largos, comentarios o mensajes de error en español, capas mezcladas, archivos fuera de lugar, SQL crudo, secretos hardcodeados. Frases típicas que la disparan: "audita este repo", "qué tan lejos está del estándar", "revisa la deuda técnica de este módulo", "qué habría que arreglar acá", "este código es viejo y no sigue las convenciones", "dónde estamos incumpliendo el estándar", "auditoría de código legacy".
allowed-tools: Read, Bash, Glob, Grep
---

# Auditoría contra el estándar del equipo

Recorre código **ya existente** y reporta dónde se aparta del estándar. Es la contraparte
deliberada de los hooks de pre-commit: esos solo miran los archivos que un commit toca (para no
bloquear por deuda histórica), así que la foto completa hay que pedirla explícitamente — esta
skill es esa foto.

## Reglas importantes

- **No modifiques nada.** Ni código, ni configuración, ni commits. El producto es un informe.
  Si el usuario quiere arreglos, es un paso posterior y explícito, módulo por módulo.
- **No propongas una reescritura completa.** El estándar dice que el código legacy se corrige
  cuando alguien lo toca. Un informe que pide refactorizar todo se ignora; uno que prioriza por
  riesgo y por frecuencia de cambio se usa.
- **Distingue lo mecánico de lo estructural.** Lo mecánico es objetivo (largo, idioma). Lo
  estructural es un juicio: fundaméntalo en el archivo concreto, no en una impresión general.
- **No reportes como incumplimiento lo que el estándar dejó abierto.** Manejo de errores en
  backend y consumo de API en frontend están marcados `(por definir)`: ahí la regla es "coherente
  con el repo", así que solo es hallazgo la incoherencia *interna* del repo.

## Paso 1 — Acotar el alcance

Pregunta o infiere qué auditar, en este orden de preferencia:

1. Un **módulo o carpeta** concreta (lo más útil: da un informe accionable).
2. Los archivos **modificados con más frecuencia** (donde la deuda cuesta cada semana):
   ```bash
   git log --format=format: --name-only --since=6.months \
     | grep -Ev '^$' | sort | uniq -c | sort -rn | head -30
   ```
3. El repo completo (solo si lo piden; el informe será largo y menos accionable).

Detecta el stack por lo que hay en la raíz (`pyproject.toml`, `package.json`, `manage.py`,
`dags/`) para saber qué reglas aplican.

## Paso 2 — Cargar las reglas

Busca en tu contexto el bloque **"Tier 2 references"** que el plugin `team-standards` inyecta al
inicio de la sesión: tiene las rutas absolutas de `backend-layout.md`, `frontend-layout.md`,
`data-layout.md` y `review-checklist.md`. **Lee las que apliquen al stack detectado.**

Si ese bloque no está (el plugin `team-standards` no está instalado), apóyate en el estándar que
sí esté en contexto y anótalo como limitación al inicio del informe.

## Paso 3 — Chequeos mecánicos

Si el repo ya tiene instalados los verificadores (`.standards/` en la raíz, ver skill
`setup-standards-lint`), úsalos sobre el alcance elegido — es la misma medida que usa pre-commit:

```bash
python3 .standards/check_file_length.py <archivos...>
python3 .standards/check_comment_language.py <archivos...>
```

Si no están instalados, mide lo mismo directamente:

```bash
# Archivos más largos del alcance
find <ruta> -type f \( -name '*.py' -o -name '*.ts' -o -name '*.tsx' -o -name '*.vue' \) \
  -exec wc -l {} + | sort -rn | head -20

# Señales de comentarios/mensajes en español (revisa los resultados, no los cuentes a ciegas)
grep -rn --include='*.py' --include='*.ts' --include='*.tsx' --include='*.vue' \
  -E '[áéíóúñ¿¡]' <ruta> | head -40
```

Además busca:

- **Mensajes de error y logs en español** — la regla cubre `raise`, `throw`, y líneas de log, no
  solo comentarios.
- **SQL crudo**: `execute(`, `raw(`, `text(` con string interpolado — distingue parametrizado de
  interpolado, que es el caso grave.
- **Secretos hardcodeados**: asignaciones a `token`, `password`, `api_key` con literal.

## Paso 4 — Chequeos estructurales

Aquí es donde hay que leer código, no grepear. Por cada archivo relevante del alcance:

- **Cohesión**: ¿el archivo hace una sola cosa que su nombre predice? Nombra la *segunda*
  responsabilidad cuando la encuentres — "es largo" no es un hallazgo, "además maneja el envío de
  correos" sí.
- **Capas** (backend): routers que consultan la BD, servicios que construyen errores HTTP,
  lógica de negocio en un repositorio. El test práctico: ¿ese servicio se podría llamar desde un
  DAG de Airflow sin HTTP de por medio?
- **Ubicación** (frontend): componentes de una sola vista en la carpeta compartida, o compartidos
  colgando de una vista; estructuras paralelas que compiten con la existente.
- **Migraciones** (si hay cambios de esquema en la historia reciente): ¿cada uno trae su
  migración versionada?
- **Airflow**: DAGs con estado oculto entre tareas, o que no son re-ejecutables para la misma
  fecha lógica.
- **RAG**: ingestas donde no se puede saber qué modelo de embeddings ni qué chunking se usó.

## Paso 5 — Informe

Prioriza por **riesgo × frecuencia de cambio**, no por cantidad de hallazgos. Un archivo de 900
líneas que nadie toca en un año es menos urgente que uno de 350 que se edita cada semana.

```markdown
# Auditoría de estándar: `<alcance>`

**Resumen:** <2-4 frases: tamaño del alcance, estado general, dónde está concentrada la deuda.>

## Prioridad alta — riesgo real
- **`ruta/archivo.py`** — <hallazgo concreto y por qué importa ahora> · *Arreglo:* <acción> · *Esfuerzo:* <bajo|medio|alto>

## Prioridad media — deuda que cuesta
- **`ruta/archivo.ts`** — <hallazgo> · *Arreglo:* <acción> · *Esfuerzo:* <...>

## Prioridad baja — cuando se toque el archivo
- **`ruta/archivo`** — <hallazgo>

(Omite las secciones que queden vacías.)

## Resumen mecánico
| Chequeo | Incumplimientos | Archivos más afectados |
|---------|-----------------|------------------------|
| Largo de archivo (>400) | <n> | <rutas> |
| Comentarios/mensajes no en inglés | <n> | <rutas> |
| SQL crudo interpolado | <n> | <rutas> |

## Por dónde empezar
1. <el arreglo con mejor relación impacto/esfuerzo>
2. <...>

## Qué ya está bien
<1-3 puntos, para dar contexto balanceado y no leerse como una lista de culpas.>
```

## Cierre

Termina recordando dos cosas al usuario:

- Nada de esto bloquea commits hoy: los hooks de pre-commit solo miran archivos tocados. Este
  informe es para decidir deliberadamente qué atacar, no una alarma.
- Si el repo aún no tiene los verificadores instalados, la skill `setup-standards-lint` los
  instala para que la deuda deje de crecer mientras se paga la existente.
