---
name: frontend-handoff
description: Genera, desde el contexto del backend, un brief portable y autoejecutable con las instrucciones que el frontend necesita para integrar un cambio del backend. Úsala SIEMPRE que el usuario haya desarrollado algo en el backend que requiera sincronización con el frontend: un endpoint nuevo para consumir, una capa de seguridad/autenticación agregada, parámetros o campos de respuesta nuevos o modificados en un endpoint existente, un cambio de contrato, o cualquier cambio que el frontend deba reflejar. Frases típicas que la disparan: "creé un endpoint y quiero consumirlo en el front", "genera las instrucciones para el frontend", "esto hay que sincronizarlo con el front", "agregué seguridad a este endpoint", "cambié lo que retorna este endpoint", "handoff al frontend", "qué tiene que cambiar el front por esto".
---

# Frontend Handoff (Backend → Frontend)

Esta skill corre **en el repositorio del backend**. Su único producto es un **brief**: un texto en
Markdown, listo para copiar y pegar en una sesión de Claude del repositorio de frontend. Ese brief
contiene el contrato del cambio y, embebidas, las instrucciones que el agente de frontend debe seguir
para integrarlo correctamente.

## Reglas importantes

- **No modifiques el frontend desde aquí.** Esta sesión no tiene ese repositorio. El trabajo de la
  skill termina al producir el brief.
- **Funda el contrato en el código real del backend**, no en suposiciones. Lee los modelos
  (ej. Pydantic), las firmas de los endpoints y las dependencias de seguridad antes de describir nada.
- **Si falta información** para describir el contrato con precisión (un schema, un código de error,
  el tipo de auth), **pregúntala al usuario antes de generar el brief**. Un brief incompleto produce
  una integración incorrecta.
- **Marca explícitamente si el cambio es BREAKING** (rompe el contrato actual que el frontend ya consume),
  porque eso cambia la estrategia de integración.

## Paso 1 — Identificar qué cambió

Si la sesión está en una rama de trabajo, mira el diff respecto de la base para no depender de la memoria:

```bash
git fetch --quiet origin 2>/dev/null || true
BASE=origin/main   # ajusta a la rama base real
git diff --stat "$BASE"...HEAD
git diff "$BASE"...HEAD
```

Si no hay diff claro o el cambio ya está en la base, pídele al usuario que describa el cambio o que
te indique los archivos/endpoints afectados.

Clasifica el cambio (puede ser más de uno):

- **Endpoint nuevo** a consumir.
- **Cambio en endpoint existente**: aditivo (nuevos params/campos opcionales) o **breaking**
  (cambia tipos, renombra/elimina campos, cambia rutas o vuelve obligatorio algo que no lo era).
- **Seguridad / autenticación**: nuevo requerimiento de token, scope, header, rol.
- **Otro** cambio de contrato (paginación, formato de errores, content-type, etc.).

## Paso 2 — Extraer el contrato

Para **cada** endpoint o cambio afectado, reúne lo que el frontend necesita. Lee los modelos y
dependencias reales del código; no aproximes.

- **Método y ruta** (ej. `POST /api/v1/recursos`).
- **Seguridad**: ¿requiere auth? ¿qué header/token/scope/rol? ¿cambió respecto de antes?
- **Request**: parámetros de path y query (con tipos y si son obligatorios), body (schema completo,
  campo por campo, con tipos y obligatoriedad), content-type.
- **Respuestas**: por cada código de estado relevante (200/201/4xx/5xx), el schema de la respuesta.
- **Formato de error**: estructura del cuerpo de error que el frontend debe manejar.
- **Paginación / filtros**, si aplica.
- **Ejemplos** concretos de request y response (uno feliz, y uno de error si es relevante).

## Paso 3 — Generar el brief

Rellena la plantilla de abajo y **preséntala como un único bloque copiable** (un solo fenced block),
para que el usuario pueda copiarlo entero y pegarlo en la sesión de frontend. No agregues comentarios
tuyos dentro del bloque; toda explicación tuya va fuera.

El brief tiene dos partes: **A) Contexto y contrato** (para que el frontend entienda qué cambió) y
**B) Instrucciones para el agente de frontend** (la parte autoejecutable). La Parte B es la que hace
que, al pegarse, el agente de frontend pregunte por archivos y estilos antes de tocar nada.

## Plantilla del brief

Reemplaza todos los `<...>`. Omite secciones que no apliquen.

````markdown
# 🔗 Brief de integración frontend — <título corto del cambio>

> Generado desde el backend. Pégalo en una sesión de Claude del repositorio de frontend y pídele que
> lo ejecute.

## A. Contexto y contrato

**Tipo de cambio:** <endpoint nuevo | cambio aditivo | cambio BREAKING | seguridad | otro>
**Resumen:** <2-3 frases: qué se hizo en el backend y qué debe lograr el frontend.>

### Endpoint(s) afectado(s)

#### `<MÉTODO> <ruta>`
- **Seguridad:** <ninguna | Bearer token en header Authorization | scope X | rol Y | ...>
- **Path params:** <nombre: tipo (obligatorio?) — descripción | ninguno>
- **Query params:** <nombre: tipo (obligatorio?) — descripción | ninguno>
- **Body (request):**
  ```
  <schema campo por campo: nombre: tipo (obligatorio?) — descripción>
  ```
- **Respuesta <código>:**
  ```
  <schema de la respuesta>
  ```
- **Errores:** <código: cuándo ocurre y forma del cuerpo>
- **Ejemplo request:**
  ```
  <ejemplo>
  ```
- **Ejemplo response:**
  ```
  <ejemplo>
  ```

### ⚠️ Notas de compatibilidad
<Si es BREAKING: qué consumo actual del frontend se rompe y por qué. Si es aditivo: confirmarlo.>

## B. Instrucciones para el agente de frontend

Eres el agente del repositorio de **frontend**. Tu tarea es integrar el cambio descrito arriba.
**No empieces a escribir código todavía.** Sigue este orden:

1. **Pide los archivos clave antes de escanear el repo.** Para no recorrer todo el proyecto, pregúntale
   al usuario qué archivos debes leer/modificar/considerar. Sugiere explícitamente estas categorías y
   pide la ruta de cada una que exista:
   - Capa de cliente HTTP / servicios de API (donde se definen las llamadas).
   - Definiciones de tipos / interfaces / modelos del dominio afectado.
   - Hooks, stores o manejo de estado relacionados.
   - Componentes o páginas que consumirán o consumen este endpoint.
   - Configuración de entorno (base URL de la API, manejo de auth/token).
   - Archivos de convenciones/estilos si existen.

2. **Pregunta por estilo y consideraciones adicionales.** Antes de implementar, pregunta si hay
   convenciones, patrones, librerías (ej. de fetching o validación), o restricciones que debas
   respetar y que no se deduzcan de los archivos entregados.

3. **Implementa** usando como base **solo** los archivos que el usuario indicó (más los que esos
   referencien y necesites leer). Cubre lo que aplique: tipos/interfaces, método en el cliente de API,
   hook/estado, integración en componente, manejo de los errores documentados, y configuración de
   entorno/auth si cambió. Respeta el estilo existente.

4. **Si durante la integración detectas que el backend está mal o es insuficiente** —por ejemplo, un
   campo que falta, un formato de error inconsistente, un problema de CORS, un desajuste de auth, o un
   contrato que no calza con lo que el frontend necesita— **detente y no improvises un parche en el
   frontend.** En su lugar, devuelve una sección clara titulada **"⚠️ Cambios requeridos en el backend"**,
   con cada problema, por qué bloquea, y qué cambio sugieres en el backend. El usuario llevará eso de
   vuelta a la sesión del backend.

5. **Cierre:** resume qué archivos creaste/modificaste y cualquier paso manual pendiente
   (variables de entorno nuevas, regenerar tipos, etc.).
````

## Después de presentar el brief

Tras mostrar el bloque, dile al usuario en una línea: que lo copie y lo pegue en la sesión de frontend
pidiendo "ejecuta este brief", y que si vuelve con una sección "Cambios requeridos en el backend",
puede traértela a esta sesión para resolverla.
