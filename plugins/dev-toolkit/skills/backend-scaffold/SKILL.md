---
name: backend-scaffold
description: Crea un endpoint o módulo de backend respetando la separación por capas del estándar del equipo (routers → services → repositories en FastAPI, o el layout estándar de app en Django). Úsala cuando el usuario quiera agregar un endpoint, un recurso o un módulo nuevo al backend y quiera que quede bien ubicado desde el principio. Frases típicas que la disparan: "crea un endpoint para X", "agrega un módulo de Y", "necesito un CRUD de Z", "arma la estructura para este recurso", "scaffolding del backend", "dónde debería ir este endpoint", "crea el servicio y el repositorio para esto". Aplica a trabajo **acotado**: si la funcionalidad es grande, toca varias capas o todavía no está definida su forma, primero usa `feature-plan` y vuelve acá para construir cada etapa.
---

# Scaffolding de backend por capas

Crea la estructura de un endpoint o módulo nuevo **donde el estándar dice que va**, en vez de
dejarlo donde sea más rápido. La mayor parte del valor está en el Paso 1: entender qué convención
sigue *este* repo antes de escribir nada.

## Reglas importantes

- **Sigue el repo, no la plantilla.** Si el repo ya tiene una estructura, replícala aunque
  difiera del árbol de referencia. Nunca abras una estructura paralela que compita con la
  existente.
- **No inventes las convenciones abiertas.** El manejo de errores está marcado `(por definir)` en
  el estándar: usa el patrón que ya tenga el repo y no introduzcas un tercero. Si el repo no tiene
  ninguno, pregunta antes de elegir.
- **Autorización obligatoria.** Todo endpoint que exponga datos lleva su control de autorización,
  con el mecanismo que use el repo. No dejes un endpoint abierto porque "todavía no está enlazado
  en la UI".
- **ORM, no SQL crudo.** El SQL crudo es excepcional: requiere justificación en un comentario y
  siempre parametrizado.
- **Código y mensajes en inglés**, incluidos los mensajes de error y los logs.

## Paso 1 — Reconocer el repo

Antes de crear archivos, establece qué convención seguir:

```bash
ls
test -f manage.py && echo "Django" || true
grep -rl "FastAPI(" --include='*.py' . 2>/dev/null | head -3
```

Luego mira **un módulo existente y parecido** al que vas a crear, de punta a punta, para copiar su
forma: cómo se nombran los archivos y las rutas, cómo se inyectan dependencias, cómo se validan
los inputs, cómo se manejan los errores, cómo se estructuran los tests.

Lee también `backend-layout.md` — su ruta absoluta viene en el bloque **"Tier 2 references"** que
el plugin `team-standards` inyecta al inicio de la sesión. Si ese bloque no está, apóyate en el
estándar en contexto y en el módulo de referencia que acabas de leer.

Si el repo mezcla convenciones (por ejemplo, un módulo por capas y otro todo en un archivo),
**pregunta cuál es la vigente** antes de elegir.

## Paso 2 — Definir el contrato antes de escribir

Confirma con el usuario, sin asumir:

- **Recurso y operaciones**: ¿qué entidad, y qué operaciones realmente se necesitan ahora? No
  generes un CRUD completo si solo se pide leer (YAGNI).
- **Forma del request y del response**, campo por campo.
- **Autorización**: quién puede llamar a cada operación, y con qué mecanismo del repo.
- **Persistencia**: ¿el modelo ya existe? Si no, esto implica **migración versionada**.
- **Casos de error** que el consumidor debe poder distinguir.

Si el pedido viene de un brief de `backend-handoff`, el contrato ya está ahí: evalúalo en vez de
tomarlo literal (puede pedir campos que no corresponde exponer).

## Paso 3 — Crear las capas

### FastAPI

Estructura de referencia (ajústala a la del repo):

| Capa | Qué crear | Qué NO debe tener |
|------|-----------|-------------------|
| `api/` (router) | Ruta, schemas de request/response, dependencias de auth, códigos de estado | Queries, reglas de negocio |
| `services/` | Reglas de negocio, orquestación, límites de transacción | Nada de HTTP |
| `repositories/` | Queries y persistencia del agregado | Reglas de negocio |
| `schemas/` | Modelos pydantic de entrada/salida | Lógica |
| `models/` | Modelos ORM | Lógica de presentación |

El test que valida que las capas quedaron bien: **el servicio debe poder llamarse desde una tarea
de Airflow o un script de CLI, sin HTTP de por medio.** Si no se puede, algo de HTTP se filtró
hacia abajo.

### Django

Sigue el layout estándar de app (`models.py`, `views.py`, `serializers.py`, `urls.py`). **No
retrofitees** el árbol de FastAPI sobre una app Django. Mantén las vistas delgadas; la lógica que
no pertenece a un modelo va en un `services.py` dentro de la app.

### Si el esquema cambia

Genera la migración versionada (Alembic o Django) en el mismo cambio, y planifica el rollout
no-breaking: agregar columna → desplegar código → backfill → recién entonces eliminar la vieja.
Indexa las claves foráneas y las columnas por las que efectivamente se filtra.

## Paso 4 — Verificar antes de cerrar

- ¿Cada archivo nuevo quedó **donde están sus pares**?
- ¿Ningún archivo nuevo excede el largo del estándar (300 advierte / 400 límite)? Si uno ya nace
  cerca del límite, es señal de que hay dos responsabilidades juntas.
- ¿Todo endpoint nuevo tiene autorización?
- ¿Identificadores, comentarios, docstrings y mensajes de error en inglés?
- ¿Los tests siguen la forma del módulo de referencia?
- ¿Corre lo que se pueda correr localmente (levantar la app, ejecutar los tests del módulo)?

## Paso 5 — Reportar

Cierra con: archivos creados y en qué capa quedó cada uno, el contrato final expuesto, si hay
migración pendiente de aplicar, variables de entorno nuevas, y qué quedó deliberadamente fuera
del alcance.

Si durante el scaffolding detectaste que el repo se aparta del estándar en la zona que tocaste,
menciónalo en una línea pero **no lo arregles acá** — el estándar pide cambiar solo lo que la
tarea necesita. Para verlo completo está la skill `standards-audit`.
