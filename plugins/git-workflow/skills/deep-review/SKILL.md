---
name: deep-review
description: Revision profunda y multiagente de una rama antes de mergear, con 5 especialistas en paralelo (seguridad, arquitectura, clean code, eficiencia/escalabilidad, correccion/casos borde/tests) y un agente consolidador pragmatico que decide que es critico, recomendable o nice-to-have. Usala SOLO cuando el usuario pida explicitamente varios angulos o multiples agentes para una revision — "revision profunda", "revision con multiples agentes", "quiero varios angulos de esta revision", "revision exhaustiva de la rama", "audita esta rama con distintos especialistas", "revisemos esto con un agente de seguridad, uno de arquitectura...". Para una revision normal de una rama antes de mergear usa `pre-merge-review`: esta skill es deliberadamente mas cara (5-6 llamadas a agente) y solo vale la pena en ramas grandes o riesgosas.
---

# Deep Review

Revision multiagente de una rama de trabajo **antes** de integrarla a la rama base. Esta skill reparte el juicio en
especialistas independientes que corren en paralelo y son deliberadamente minuciosos — "exagerados" en su
busqueda — y termina con un agente consolidador que hace lo contrario: prioriza con pragmatismo, pensando en
que es lo minimo necesario para que la funcionalidad avance de forma segura, sin convertir la revision en
una propuesta de reestructuracion.

## Reglas importantes

- **No modifiques codigo.** Esta skill solo produce un informe. No edites archivos, no hagas commits, no ejecutes el merge.
- **Es mas cara que `pre-merge-review`.** Corre 5-6 llamadas a agente (los especialistas seleccionados en
  paralelo, mas el consolidador). Reservala para cuando el usuario la pida explicitamente o la rama sea lo
  bastante grande/riesgosa para justificar el costo — no la ofrezcas como default.
- **Workflow corre en background.** Avisa al usuario que la revision se esta ejecutando y que el informe
  llegara como notificacion; no bloquees ni inventes un resultado mientras tanto.

## Paso 1 — Contexto y alcance

Determina la rama actual y la rama base (`origin/main`/`master`, o la que el usuario indique).

```bash
git fetch --quiet origin 2>/dev/null || true
git rev-parse --abbrev-ref HEAD
git symbolic-ref --quiet refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'
```

Si el usuario pidió acotar la revision a una carpeta o path (ej. "revisa solo `/src`", "acota al backend"),
guarda ese path — se usara para filtrar el diff.

## Paso 2 — Elegir especialistas

Los 5 especialistas disponibles, por `key`:

| key | Enfoque |
| --- | --- |
| `security` | Seguridad: inputs, inyeccion, secretos, autorizacion, exposicion de datos |
| `architecture` | Capas, ubicacion de archivos, limites, consistencia con patrones del repo |
| `clean-code` | Nombres, funciones cohesionadas, duplicacion, codigo muerto, alcance del diff |
| `efficiency-scalability` | Complejidad, N+1, indices, paginacion/batching, comportamiento bajo carga |
| `correctness-edge-cases` | Bugs logicos, casos borde, concurrencia, cobertura de tests |

Por defecto corren los 5. Si el usuario pide excluir o incluir solo algunos ("sin el de eficiencia",
"solo seguridad y arquitectura"), arma la lista de `key`s correspondiente — el resto queda fuera y el
informe final lo declara explicitamente para que nadie asuma que esa dimension fue evaluada.

## Paso 3 — Recolectar el diff

Usa el operador de tres puntos y si hay un path acotado agregalo al final:

```bash
BASE=origin/main   # ajustado segun el Paso 1

# Diff completo
git diff "$BASE"...HEAD

# Diff acotado a un path, si el usuario lo pidio
git diff "$BASE"...HEAD -- src/
```

Calcula este diff **una sola vez**: se reutiliza igual para todos los especialistas, no lo recalculan ellos
por su cuenta (evita inconsistencias entre informes y gasto redundante).

## Paso 4 — Ejecutar el workflow

Invoca la herramienta `Workflow` con:

- `scriptPath`: `${CLAUDE_SKILL_DIR}/scripts/deep-review-workflow.js`
- `args`:
  - `currentBranch`, `baseBranch`: los detectados en el Paso 1.
  - `diff`: el texto del diff del Paso 3.
  - `path`: el path acotado si el usuario pidio uno, o `undefined`/omitido si es toda la rama.
  - `agents`: el arreglo de `key`s del Paso 2, o `undefined`/omitido para correr los 5.

El script reparte los especialistas seleccionados en paralelo (fase "Especialistas") y luego un agente
consolidador (fase "Consolidacion") que cruza y deduplica hallazgos repetidos entre especialistas y los
clasifica en **Critico / Recomendable / Nice-to-have**.

## Paso 5 — Entregar el resultado

Cuando el workflow termine, comparte el informe del consolidador tal cual — es el entregable final, ya
viene en markdown con la estructura Critico/Recomendable/Nice-to-have, que especialistas corrieron/se
omitieron, y el alcance (toda la rama o acotado a un path). No lo resumas ni lo reescribas; si el usuario
pide profundizar en un hallazgo puntual, ahi si elabora sobre el.
