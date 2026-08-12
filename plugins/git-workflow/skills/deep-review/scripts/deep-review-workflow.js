export const meta = {
  name: 'deep-review',
  description: 'Revision profunda de una rama: especialistas en paralelo (seguridad, arquitectura, clean code, eficiencia, correctness) mas un consolidador pragmatico',
  phases: [
    { title: 'Especialistas' },
    { title: 'Consolidacion' },
  ],
}

// Same severity scale pre-merge-review already uses — keep the team on one vocabulary.
const SEVERITY_SCALE = `- 🔴 Bloqueante — debe arreglarse antes de mergear (bug, riesgo de seguridad, regresion).
- 🟠 Importante — deberia arreglarse, pero no necesariamente bloquea (deuda real, riesgo medio).
- 🟡 Menor / sugerencia — mejora opcional (estilo, micro-optimizacion, nit).`

// Each specialist gets one guiding question and an explicit "do not report" boundary,
// so five agents reading the same diff don't just restate the same finding five times.
const SPECIALISTS = [
  {
    key: 'security',
    label: 'Seguridad',
    focus: `Enfocate SOLO en seguridad: validacion y saneamiento de inputs, inyeccion (SQL/comando/plantillas),
secretos hardcodeados, autorizacion en cada endpoint que expone datos, exposicion de datos sensibles en logs
o respuestas. No comentes legibilidad, arquitectura ni eficiencia — de eso se encargan otros especialistas.`,
  },
  {
    key: 'architecture',
    label: 'Arquitectura de software',
    focus: `Enfocate SOLO en arquitectura: separacion de capas (router/servicio/repositorio), si cada archivo 
nuevo esta donde estan sus pares o abre una estructura paralela, limites entre
capas (un router que consulta la BD, un servicio que arma respuestas HTTP), consistencia con los patrones ya
presentes en el repo. NO comentes nombres, legibilidad ni duplicacion de codigo — eso es del especialista
clean-code.`,
  },
  {
    key: 'clean-code',
    label: 'Buenas practicas y clean code',
    focus: `Enfocate SOLO en legibilidad local: nombres claros, funciones pequeñas y cohesionadas, duplicacion,
codigo muerto o abstracciones sin uso real (YAGNI), y si el diff trae refactors no relacionados con la tarea.
NO comentes ubicacion de archivos ni limites entre capas — eso es del especialista architecture.`,
  },
  {
    key: 'efficiency-scalability',
    label: 'Eficiencia y escalabilidad',
    focus: `Enfocate SOLO en eficiencia y escalabilidad: complejidad innecesaria, queries N+1, falta de indices,
llamados repetidos evitables, cargas en memoria evitables, falta de paginacion o batching, comportamiento
bajo carga o con volumenes grandes.`,
  },
  {
    key: 'correctness-edge-cases',
    label: 'Correccion, casos borde y tests',
    focus: `Enfocate SOLO en correccion funcional: bugs logicos, manejo de nulos/vacios, limites, concurrencia,
fallos de red/IO, estados intermedios, inputs inesperados. Revisa tambien si lo nuevo tiene tests que cubran
el comportamiento (no solo la implementacion) y si faltan casos borde en esos tests.`,
  },
]

const FINDINGS_SCHEMA = {
  type: 'object',
  properties: {
    agent: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          file: { type: 'string' },
          line: { type: 'string' },
          severity: { type: 'string', enum: ['🔴 Bloqueante', '🟠 Importante', '🟡 Menor / sugerencia'] },
          description: { type: 'string' },
          suggestion: { type: 'string' },
        },
        required: ['file', 'severity', 'description'],
      },
    },
  },
  required: ['agent', 'findings'],
}

function specialistPrompt(specialist, scopeNote) {
  return `Eres un revisor de codigo especialista en ${specialist.label}, revisando la rama \`${args.currentBranch}\`
contra \`${args.baseBranch}\`. ${scopeNote}

${specialist.focus}

Se exhaustivo y minucioso: reporta TODO lo que encuentres dentro de tu enfoque, sin autocensurarte por
pragmatismo — para eso existe un agente consolidador despues de ti. Fundamenta cada hallazgo en el diff real
(archivo y linea concretos), nunca en suposiciones. Usa esta escala de severidad:
${SEVERITY_SCALE}

Diff a revisar:
\`\`\`diff
${args.diff}
\`\`\`

Devuelve tus hallazgos con el campo "agent" = "${specialist.key}". Si no encuentras nada dentro de tu
enfoque, devuelve un arreglo de hallazgos vacio — no inventes problemas para justificar tu paso.`
}

function consolidatorPrompt(reports, selected, skipped, scopeNote) {
  const skippedLabels = skipped.length ? skipped.map(s => s.label).join(', ') : 'ninguno — corrieron los 5.'
  return `Eres el agente consolidador de una revision profunda de la rama \`${args.currentBranch}\` contra
\`${args.baseBranch}\`. Recibiste ${reports.length} informes de especialistas independientes, cada uno
exhaustivo y sin filtro de pragmatismo dentro de su propio enfoque.

${scopeNote}

Especialistas que SI corrieron: ${selected.map(s => s.label).join(', ')}.
Especialistas que NO corrieron en esta ejecucion (no asumas que esas dimensiones fueron evaluadas):
${skippedLabels}

Tu trabajo es lo opuesto al de los especialistas: se pragmatico. Para cada hallazgo preguntate "¿esto es
realmente necesario para que esta funcionalidad puntual avance de forma segura?" — no conviertas la revision
en una propuesta de reestructuracion. Antes de priorizar, cruza los informes: si dos o mas especialistas
senalan el mismo archivo/linea, fusiona esos hallazgos en uno solo y dilo explicitamente.

Clasifica cada hallazgo sobreviviente en exactamente uno de estos 3 baldes:
- Critico: bloquea avanzar con seguridad (bug real, riesgo de seguridad, regresion, algo caro de revertir).
- Recomendable: vale la pena resolverlo en este cambio, pero no bloquea.
- Nice-to-have: mejora el codigo a futuro, no es necesario para esta funcionalidad puntual.

Informes de los especialistas (JSON):
${JSON.stringify(reports, null, 2)}

Entrega un informe en markdown con esta estructura exacta:

# Revision profunda: \`${args.currentBranch}\` -> \`${args.baseBranch}\`

**Especialistas evaluados:** <lista> · **Especialistas omitidos:** <lista o "ninguno">
**Alcance:** <toda la rama | acotado a \`${args.path || ''}\`>

## Critico
<hallazgos o "Sin hallazgos criticos.">

## Recomendable
<hallazgos o "Sin hallazgos recomendables.">

## Nice-to-have
<hallazgos o "Sin hallazgos.">

## Hallazgos fusionados
<que hallazgos venian senalados por mas de un especialista, o "Ninguno.">
`
}

const requested = args && args.agents
const selected = requested ? SPECIALISTS.filter(s => requested.includes(s.key)) : SPECIALISTS
const skipped = SPECIALISTS.filter(s => !selected.includes(s))

const scopeNote = args.path
  ? `El diff ya viene acotado a la ruta \`${args.path}\`. Cambios fuera de esa ruta no estan incluidos — no
asumas nada sobre ellos.`
  : 'El diff cubre toda la rama, sin acotar a una ruta.'

log(`Corriendo ${selected.length}/${SPECIALISTS.length} especialistas: ${selected.map(s => s.key).join(', ')}`)

phase('Especialistas')

const reports = await parallel(selected.map(specialist => async () => {
  const result = await agent(specialistPrompt(specialist, scopeNote), {
    label: specialist.key,
    phase: 'Especialistas',
    schema: FINDINGS_SCHEMA,
  })
  return result ? { ...result, label: specialist.label } : null
}))

const validReports = reports.filter(Boolean)

phase('Consolidacion')

const consolidation = await agent(consolidatorPrompt(validReports, selected, skipped, scopeNote), {
  label: 'consolidator',
  phase: 'Consolidacion',
})

return consolidation
