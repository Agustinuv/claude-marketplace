---
name: backend-handoff
description: Genera, desde el contexto del frontend, un brief portable con lo que el backend debe construir o cambiar para que el frontend pueda avanzar. Úsala SIEMPRE que, trabajando en el frontend, el usuario necesite algo del backend que todavía no existe o no calza: un endpoint que falta, campos que no vienen en la respuesta, un filtro o paginación que no está, un formato de error inconsistente, un problema de auth o CORS. Frases típicas que la disparan: "necesito un endpoint para esto", "al back le falta devolver X", "pide esto al backend", "genera las instrucciones para el backend", "esto lo tiene que cambiar el back", "handoff al backend", "qué le tengo que pedir al backend". También aplica si pide copiar el brief al portapapeles.
---

# Backend Handoff (Frontend → Backend)

Esta skill corre **en el repositorio del frontend**. Su único producto es un **brief**: un texto
en Markdown listo para copiar y pegar en una sesión de Claude del repositorio de backend.

Es el espejo de `frontend-handoff`, con una diferencia importante: allá se **reporta** un contrato
que ya existe; acá se **pide** algo que todavía no existe. Por eso el brief debe justificar la
necesidad con el código real del frontend, no solo describir el endpoint soñado.

## Reglas importantes

- **No modifiques el backend desde aquí.** Esta sesión no tiene ese repositorio. El trabajo de la
  skill termina al producir el brief.
- **Funda la necesidad en el código real del frontend**: qué componente/vista lo necesita, qué
  datos muestra, qué ya intenta consumir. Un pedido sin ese anclaje produce un endpoint que no
  calza con lo que la UI realmente requiere.
- **Distingue "falta" de "está mal".** Un endpoint inexistente y un endpoint que devuelve un
  formato inconsistente son pedidos distintos, y el segundo puede ser breaking para otros
  consumidores.
- **No diseñes el interior del backend.** Pide el **contrato** (ruta, params, forma de la
  respuesta, errores), no la implementación: cómo se organiza en capas, qué query usa o cómo
  maneja las excepciones lo decide el backend según su propio estándar.
- **Si el frontend puede resolverlo solo, dilo.** Antes de generar el brief, verifica que lo que
  falta no esté ya disponible en otro endpoint o derivable en el cliente. No generes un pedido al
  backend para algo que el frontend ya tiene.

## Paso 1 — Establecer qué se necesita y por qué

Revisa el código que motiva el pedido: el componente o vista, la capa de cliente HTTP, los tipos
del dominio afectado. Si hay una rama de trabajo, el diff ayuda a ubicar el contexto:

```bash
git fetch --quiet origin 2>/dev/null || true
BASE=origin/main   # ajusta a la rama base real
git diff --stat "$BASE"...HEAD
```

Clasifica el pedido (puede ser más de uno):

- **Endpoint que falta** por completo.
- **Campos o datos que faltan** en un endpoint existente (pedido aditivo).
- **Cambio de forma** en un endpoint existente: tipos, nombres, estructura — potencialmente
  **breaking** para otros consumidores.
- **Filtros, ordenamiento o paginación** que la vista necesita y el endpoint no ofrece.
- **Errores**: formato inconsistente, códigos que no distinguen casos que la UI debe distinguir.
- **Auth / CORS**: el frontend no puede autenticar o el navegador bloquea la llamada.
- **Rendimiento**: la vista necesita N llamadas donde debería bastar una.

Si falta información para justificar el pedido (qué muestra exactamente la vista, qué pasa en el
caso vacío, qué debe ver un usuario sin permisos), **pregúntasela al usuario antes de generar el
brief**.

## Paso 2 — Especificar el contrato pedido

Para cada pedido, arma la especificación desde la necesidad de la UI:

- **Qué muestra o hace la vista** — es lo que justifica cada campo pedido.
- **Datos requeridos**: campo por campo, con tipo, si es obligatorio, y **para qué se usa en la
  UI**. Un campo sin uso concreto no se pide.
- **Volumen y filtros**: cuántos registros espera la vista, qué filtros u ordenamientos aplica el
  usuario, si necesita paginación.
- **Casos que la UI debe distinguir**: vacío, sin permisos, no encontrado, en proceso. Cada uno
  necesita ser distinguible en la respuesta o en el código de estado.
- **Forma sugerida** de la respuesta (como propuesta, no como imposición).
- **Qué hace hoy el frontend** mientras esto no existe: nada, un workaround, datos mock. Esto le
  dice al backend qué urgencia real tiene.

## Paso 3 — Generar el brief

Rellena la plantilla y **preséntala como un único bloque copiable** (un solo fenced block), sin
comentarios tuyos dentro; toda explicación va fuera del bloque.

## Plantilla del brief

Reemplaza todos los `<...>`. Omite secciones que no apliquen.

````markdown
# 🔗 Brief de pedido al backend — <título corto>

> Generado desde el frontend. Pégalo en una sesión de Claude del repositorio de backend y pídele
> que lo ejecute.

## A. Qué necesita el frontend y por qué

**Tipo de pedido:** <endpoint nuevo | campos faltantes | cambio de forma (BREAKING) | filtros/paginación | errores | auth/CORS | rendimiento>
**Vista / componente que lo necesita:** <ruta del archivo y qué muestra>
**Situación actual:** <qué hace hoy el frontend sin esto: nada / workaround / mock>

### Pedido

#### <MÉTODO sugerido> <ruta sugerida>

- **Para qué:** <qué renderiza o permite hacer la UI con esto>
- **Datos requeridos:**
  ```
  <campo: tipo (obligatorio?) — para qué se usa en la UI>
  ```
- **Filtros / paginación:** <qué filtra u ordena el usuario, volumen esperado | no aplica>
- **Casos que la UI debe poder distinguir:**
  ```
  <caso: cómo debería reflejarse en la respuesta o en el status>
  ```
- **Forma sugerida de la respuesta** (propuesta, ajústala a la convención del backend):
  ```
  <ejemplo de respuesta>
  ```

### ⚠️ Notas de compatibilidad
<Si es un cambio de forma: qué consume hoy el frontend y qué se rompería. Si es aditivo, confirmarlo.>

## B. Instrucciones para el agente de backend

Eres el agente del repositorio de **backend**. Tu tarea es evaluar e implementar el pedido de
arriba. **No empieces a escribir código todavía.** Sigue este orden:

1. **Evalúa el pedido antes de implementarlo.** No lo tomes como especificación final: el
   frontend describió una necesidad, no un diseño de backend. Revisa en particular si:
   - Ya existe un endpoint que cubre esto (total o parcialmente) y basta extenderlo.
   - Algún campo pedido expone datos que ese usuario no debería ver, o mueve al cliente una
     regla de negocio que pertenece al backend. **Si es así, dilo y propone la alternativa** en
     vez de implementarlo tal cual.
   - El pedido rompe el contrato de otros consumidores ya existentes.

2. **Pide los archivos clave antes de escanear el repo.** Pregúntale al usuario qué archivos
   debes leer/modificar, sugiriendo estas categorías y pidiendo la ruta de cada una que exista:
   - Routers/endpoints del dominio afectado.
   - Servicios y repositorios (o `views.py`/`serializers.py` en Django) de ese dominio.
   - Modelos ORM y schemas de request/response.
   - Dependencias de autenticación/autorización.
   - Migraciones, si el pedido implica cambio de esquema.

3. **Pregunta por convenciones no evidentes.** Antes de implementar, pregunta por patrones que
   debas respetar y no se deduzcan de los archivos entregados (manejo de errores, paginación,
   naming de rutas).

4. **Implementa respetando el estándar del equipo**: separación por capas, ORM (no SQL crudo sin
   justificar y parametrizar), configuración desde variables de entorno, y **autorización
   obligatoria en todo endpoint que exponga datos**. Si el cambio toca el esquema, modifica el
   modelo ORM y **pídele al usuario que corra el comando de migraciones del repo** (`task
   migrate`, `docker compose run --rm <servicio> alembic revision --autogenerate -m "..."` +
   `alembic upgrade head`, `manage.py makemigrations && migrate` — revisa antes qué usa el repo).
   No escribas el archivo de revisión a mano ni ejecutes las migraciones tú; revisa el archivo
   generado cuando el usuario te lo devuelva.

5. **Devuelve el contrato final implementado**, campo por campo y con los códigos de error, en una
   sección **"✅ Contrato implementado"** — incluso si terminó distinto a lo pedido, y sobre todo
   si terminó distinto. El usuario lo llevará de vuelta al frontend para integrarlo.

6. **Cierre:** resume qué archivos creaste/modificaste, el comando de migración exacto que queda
   pendiente de correr (si el esquema cambió), y cualquier variable de entorno nueva.
````

## Paso 4 — Copiar el brief al portapapeles

Guarda el brief final en un archivo temporal y cópialo con:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/copy_to_clipboard.sh <archivo-temporal>
```

- Si el script confirma éxito (`OK: ...`), avisa brevemente cómo se copió.
- Si falla (`WARN: ...`), dilo explícitamente y por qué, para que el usuario copie a mano.

Siempre muestra el brief completo en tu respuesta, aunque la copia haya tenido éxito.

## Después de presentar el brief

En una línea: que ya está en el portapapeles (o que lo copie a mano), que lo pegue en la sesión de
backend pidiendo "ejecuta este brief", y que cuando vuelva con la sección **"✅ Contrato
implementado"** puede traerla acá para hacer la integración en el frontend.
