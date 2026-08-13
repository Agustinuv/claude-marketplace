---
name: feature-plan
description: Prepara el plan de implementación de una funcionalidad grande antes de escribir código: releva los componentes existentes que el cambio va a tocar, entrevista al desarrollador sobre alcance, expectativas y restricciones, contrasta contra el estándar del equipo y deja el plan escrito en un archivo. Úsala cuando el usuario quiera planificar antes de implementar, no cuando ya quiera el código. Frases típicas que la disparan: "ayúdame a planificar esto", "quiero armar una funcionalidad grande", "cómo abordo esta feature", "planifiquemos antes de implementar", "arma un plan de implementación", "hazme las preguntas que necesites antes de empezar", "qué componentes va a afectar lo que quiero hacer", "quiero levantar bien los requisitos", "esto es grande, no empieces a codear todavía". No la uses para revisar un cambio ya escrito (eso es `pre-merge-review`) ni para crear un módulo acotado (eso es `backend-scaffold`).
---

# Plan de una funcionalidad grande

El producto de esta skill es **un plan escrito en un archivo**, no código. Sirve para funcionalidades
que tocan varios módulos o capas, donde empezar a codear con la primera idea sale caro.

El valor no está en redactar el plan: está en **lo que se averigua antes**. Un plan hecho sin
relevar el código existente y sin acordar el alcance con el desarrollador es una lista de deseos
prolija.

## Reglas importantes

- **No escribas código de implementación en esta skill.** Su trabajo termina con el plan escrito y
  aprobado. Si el usuario quiere avanzar, que lo pida explícitamente (o usa `backend-scaffold` para
  la estructura).
- **Compone con el plan mode, no lo reemplaza.** Si la sesión está en plan mode, esa capacidad ya
  cubre la exploración read-only y la propuesta final: no la dupliques. Lo que esta skill aporta y el
  plan mode no tiene es el **Paso 2** (la entrevista) y el **Paso 3** (el contraste con el estándar
  del equipo) — invierte el esfuerzo ahí.
- **Releva primero, pregunta después.** Nunca abras la entrevista antes de haber leído el código.
  **Nunca preguntes algo que el repositorio ya responde**: eso convierte la entrevista en un
  formulario y quema la paciencia del usuario en lo que menos importa.
- **Pregunta poco y que cada pregunta cambie el plan.** Máximo ~3 tandas de hasta 4 preguntas. Si
  una respuesta no cambiaría nada del plan, no la preguntes: asume el default y anótalo en
  **Supuestos**.
- **Ofrece siempre una recomendación.** Cada pregunta va con opciones concretas y la opción que
  recomiendas marcada como tal. El usuario debe poder aprobar, no diseñar.
- **No inventes las convenciones abiertas.** Si la feature toca el manejo de errores del backend o
  las llamadas a API del frontend, el estándar las marca `(por definir)`: usa lo que ya tenga el
  repo y, si no hay nada, regístralo en **Decisiones abiertas para el equipo** en vez de elegir por
  el equipo.
- **Etapas entregables, no capas.** "Migración → servicio → endpoint → UI" no es un plan por
  etapas: es la ruta crítica de una sola etapa. Cada etapa debe poder mergearse y verificarse por sí
  sola.
- **El plan se escribe en inglés** si va a vivir en el repositorio, como cualquier otro archivo
  versionado. La conversación con el usuario sigue en su idioma.

## Paso 0 — ¿Ya hay un plan?

Antes de todo, comprueba si esta funcionalidad ya se planificó: reentrevistar al usuario sobre algo
que ya decidió es el peor resultado posible de esta skill.

```bash
ls docs/plans/ 2>/dev/null || ls docs/ 2>/dev/null | head -20
```

Si existe un plan para esta feature, **léelo y trabaja sobre él**: retoma sus decisiones ya tomadas,
pregunta solo por lo que cambió y actualiza el archivo en vez de crear otro.

## Paso 1 — Relevar los componentes existentes

Establece qué hay hoy y qué de eso va a tener que interactuar con el cambio. Ubica el stack y el
layout real del repo:

```bash
ls
test -f manage.py && echo "Django" || true
grep -rl "FastAPI(" --include='*.py' . 2>/dev/null | head -3
test -f package.json && grep -o '"\(next\|vue\|react\)"' package.json | sort -u
```

Luego recorre, según lo que la feature vaya a tocar:

- **Backend**: routers/endpoints del dominio, servicios y repositorios (o `views.py`/`serializers.py`),
  modelos ORM y schemas, dependencias de autenticación/autorización.
- **Datos**: modelos y migraciones existentes del dominio, DAGs de Airflow que lean o escriban esas
  tablas, colecciones de Qdrant y su configuración de embeddings/chunking si hay RAG.
- **Frontend**: vistas y componentes que muestran ese dominio, capa de cliente HTTP, tipos, estado
  compartido (stores) que quedaría desincronizado.
- **Transversal**: configuración/variables de entorno, tests que cubren lo que vas a mover, y
  **quién más consume** lo que vas a cambiar (otros endpoints, otros clientes, un DAG).

Mira **un módulo existente y parecido de punta a punta** para saber qué forma debe tener lo nuevo.
Si algún archivo relevante ya está cerca del límite de 400 líneas, anótalo: condiciona dónde puede
crecer el código.

El resultado de este paso es un **mapa de impacto**: por cada componente, qué cambia y qué riesgo
tiene. Ese mapa es también la materia prima de las preguntas del Paso 2 — las buenas preguntas
salen de las ambigüedades que el código dejó abiertas, no de una lista genérica.

Si el repositorio es grande y el barrido va a ser amplio, delega el relevamiento a un subagente de
exploración y quédate con el mapa; la entrevista la haces tú, en esta sesión.

## Paso 2 — Entrevistar al desarrollador

Usa `AskUserQuestion`, en tandas, cerrando cada tanda antes de abrir la siguiente. Antes de
preguntar, **enseña el mapa de impacto en dos o tres líneas**: el usuario responde mucho mejor
cuando ya sabe qué encontraste.

Ejes a cubrir, en este orden de prioridad — omite el que el código ya haya contestado:

1. **Alcance**: qué entra en esta iteración y, sobre todo, **qué queda explícitamente afuera**. El
   fuera-de-alcance es la parte del plan que más discusión ahorra después.
2. **Expectativas**: quién usa esto, qué debe poder hacer, cómo se ve "listo". Si hay un
   comportamiento observable en la UI, pídelo en concreto.
3. **Restricciones**: compatibilidad con lo que ya está en producción, datos existentes que hay que
   migrar o preservar, volumen y rendimiento esperado, roles y permisos, plazos o entregas parciales.
4. **Decisiones técnicas abiertas**: solo aquellas donde el repo no marca el camino y hay más de una
   opción viable. Preséntalas con el trade-off en una línea, no con una disertación.

Cuando detectes un supuesto que el usuario probablemente no consideró (un consumidor que se rompe,
un caso vacío, un dato que hay que backfillear), **plantéalo como sugerencia** en vez de esperar que
él lo pregunte. Ese es el aporte que distingue esta skill de un cuestionario.

## Paso 3 — Contrastar contra el estándar del equipo

Busca en tu contexto el bloque **"Tier 2 references"** que el plugin `team-standards` inyecta al
inicio de la sesión: tiene las rutas absolutas de `backend-layout.md`, `frontend-layout.md`,
`data-layout.md` y `review-checklist.md`. Lee **solo** las que apliquen a esta feature.

Revisa el plan contra lo que el estándar exige, y ajústalo antes de escribirlo:

- Separación por capas sin atajos: nada de routers que tocan la base ni componentes que arman HTTP
  a mano.
- ORM, no SQL crudo. Todo cambio de esquema con **migración versionada y rollout no-breaking** — si
  el plan implica renombrar o eliminar una columna en uso, tiene que partirse en etapas. Las
  migraciones las genera la herramienta (Alembic `--autogenerate` / `makemigrations`) y **las corre
  el desarrollador**: la etapa que toca el esquema debe dejar escrito el comando del repo (`task
  migrate`, `docker compose run --rm <servicio> alembic upgrade head`, …) como paso manual.
- Autorización en **todo** endpoint que exponga datos, y validación en el borde.
- Ubicación de archivos según el layout ya existente; nunca una estructura paralela. Límite de 400
  líneas por archivo como restricción de diseño, no como detalle de formato.
- Frontend: componentes de función + hooks / Composition API, Tailwind, estado local salvo que sea
  genuinamente compartido.
- Si la feature cruza backend y frontend, el plan debe indicar en qué etapa se produce el handoff y
  con qué skill (`backend-handoff` / `frontend-handoff`), no asumir que ambos lados avanzan solos.

Cualquier punto donde el estándar y lo que pidió el usuario no coincidan **se dice explícitamente**,
con la alternativa que sí cumple.

## Paso 4 — Escribir el plan

Escribe el archivo en `docs/plans/<slug-de-la-feature>.md` — o donde el repo ya guarde documentos de
diseño, si tiene un lugar propio. Confirma la ruta con el usuario si vas a crear el directorio.

Rellena la plantilla, reemplazando todos los `<...>` y omitiendo las secciones que no apliquen.
Muestra además un resumen en tu respuesta: objetivo, etapas y decisiones abiertas.

````markdown
# <Feature name>

## Goal and definition of done

<What this feature enables, and the observable condition that means it is done.>

## Scope

**In scope:** <bullets>
**Out of scope (this iteration):** <bullets — be explicit, this is the section that prevents scope creep>

## Impact map — existing components

| Component | What changes | Risk |
| --- | --- | --- |
| `<path>` | <change> | <low/medium/high + why> |

**Other consumers affected:** <endpoints, clients, DAGs that depend on what changes — or "none found">

## Decisions taken

| Decision | Choice | Why |
| --- | --- | --- |
| <topic> | <choice> | <reason, incl. what the repo already does> |

## Assumptions

<Defaults assumed without asking. Each one is a place the plan can be wrong.>

## Open decisions for the team

<Only conventions the standard marks as "por definir" that this feature touches, or choices that
outlive this feature. State the proposed direction; do not decide unilaterally.>

## Stages

Each stage is independently mergeable and verifiable.

### Stage 1 — <name>
- **Changes:** <files to create/modify>
- **Migration:** <versioned migration + non-breaking rollout, or "none">
- **Migration command (run by the developer):** <exact repo command, e.g. `task migrate` — or "n/a">
- **Verification:** <how to prove this stage works>

### Stage 2 — <name>
<...>

## Risks and rollback

| Risk | Mitigation / rollback |
| --- | --- |
| <risk> | <how it is contained> |

## Handoffs

<If the feature crosses backend/frontend: which stage produces the contract, and which handoff
skill carries it. Omit if single-repo.>
````

## Cierre

En pocas líneas: dónde quedó el plan, cuál es la primera etapa, y qué decisiones abiertas necesitan
respuesta del equipo antes de arrancar. Pregunta si quiere ajustar el plan o empezar por la etapa 1
— y no empieces sin que lo diga.
