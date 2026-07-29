---
name: audit-marketplace
description: Audita la calidad y la coherencia del marketplace completo, más allá de la validación mecánica: descripciones de skills que compiten por el mismo trigger, referencias cruzadas obsoletas, criterios duplicados que ya derivaron entre plugins, skills sin uso y plugins con responsabilidades mezcladas. Úsala cuando el usuario quiera mejorar el marketplace en vez de solo validarlo: "audita el marketplace", "qué se puede mejorar acá", "revisa si las skills se pisan entre ellas", "hay cosas duplicadas u obsoletas", "esto está bien organizado", "revisa la coherencia de los plugins", "actualiza los prompts de las skills".
allowed-tools: Read, Bash, Glob, Grep
---

# Auditoría cualitativa del marketplace

Complementa a `validate-marketplace`, que es mecánica. Esa responde "¿está bien formado?";
esta responde **"¿está bien diseñado, y sigue siendo coherente?"**.

Corre **en el repositorio del marketplace**.

## Reglas importantes

- **No modifiques nada sin confirmación.** El producto es un informe con propuestas. Aplica
  cambios solo si el usuario los aprueba, y de a uno.
- **Fundamenta cada hallazgo en archivos concretos.** "Las descripciones podrían mejorar" no es un
  hallazgo; "estas dos compiten por la frase X" sí.
- **No propongas agregar cosas.** El sesgo de una auditoría es sugerir features nuevas. El valor
  acá es lo contrario: detectar lo que sobra, lo que se pisa y lo que derivó.
- **Corre primero `validate-marketplace`** (o al menos `claude plugin validate .` y
  `python3 scripts/check_conventions.py`). Si hay fallas mecánicas, resuélvelas antes: no tiene
  sentido auditar diseño sobre algo que no valida.

## Paso 1 — Inventario

```bash
python3 -c "
import json
from pathlib import Path
manifest = json.loads(Path('.claude-plugin/marketplace.json').read_text())
for entry in manifest['plugins']:
    print(entry['name'], '->', entry['source'])
print('renames:', manifest.get('renames', {}))
"
find plugins -path '*/skills/*/SKILL.md' | sort
```

Para cada skill, extrae su `name` y su `description` completa — son el insumo de los pasos 2 y 3.

## Paso 2 — Triggers que compiten

Este es el hallazgo de mayor impacto: dos skills cuyas `description` reclaman las mismas frases
hacen que Claude elija de forma impredecible entre ellas.

- Junta todas las frases-gatillo declaradas y busca **solapamientos reales**, no temáticos. Dos
  skills sobre git no es problema; dos que ambas dicen disparar con "revisa los cambios" sí.
- Verifica que cada `description` diga **cuándo NO usarla** si hay una vecina cercana (por
  ejemplo `pre-merge-review` vs `standards-audit`: una revisa un diff antes de mergear, la otra
  audita código ya integrado).
- Compara también contra las skills que Claude Code trae de fábrica y contra otros plugins que el
  equipo tenga instalados: una skill propia que duplica una existente solo agrega ambigüedad.
- Marca descripciones vagas: si no contiene frases textuales que un usuario diría, la skill
  probablemente no se auto-invoca nunca.

## Paso 3 — Referencias cruzadas obsoletas

El estándar y las skills se nombran entre sí; los renombres las rompen en silencio.

```bash
# Nombres de skills realmente existentes
find plugins -path '*/skills/*/SKILL.md' | sed 's|.*/skills/\([^/]*\)/SKILL.md|\1|' | sort

# Menciones de skills en el estándar y en la documentación
grep -rn "skill\|SKILL" plugins/team-standards/context plugins/team-standards/references \
  CLAUDE.md README.md CONTRIBUTING.md 2>/dev/null
```

Verifica que:

- Toda skill mencionada en `team-standards.md`, en los `references/`, en `README.md`, en
  `CLAUDE.md` y en `CONTRIBUTING.md` **exista con ese nombre**.
- Todo plugin renombrado tenga su entrada en `renames`, y que las entradas viejas sigan ahí (el
  mapa es append-only).
- La documentación no describa skills o carpetas que aún no existen (o que ya no existen).

## Paso 4 — Criterios duplicados que derivaron

Los archivos no se pueden compartir entre plugins: cada plugin se instala aislado. Eso empuja a
duplicar criterios, y lo duplicado deriva.

- Ubica los casos donde una skill de un plugin **repite reglas** que son canónicas en
  `team-standards` (largo de archivo, capas, idioma, severidades). Compara los valores concretos:
  ¿el umbral que cita una skill es el mismo que el del estándar?
- Verifica que las skills que necesitan detalle lo **lean del path inyectado** por el hook de
  `team-standards` (bloque "Tier 2 references") en vez de llevar su propia copia.
- Si encuentras duplicación inevitable (scripts compartidos entre plugins distintos, como
  `copy_to_clipboard.sh`), confirma que las copias sigan siendo **idénticas**:
  ```bash
  find plugins -name 'copy_to_clipboard.sh' -exec md5 {} + 2>/dev/null \
    || find plugins -name 'copy_to_clipboard.sh' -exec md5sum {} +
  ```

## Paso 5 — Fronteras entre plugins

- ¿Cada skill está en el plugin cuya **razón de cambio** comparte? Una skill que se actualiza por
  motivos distintos al resto de su plugin probablemente esté mal ubicada.
- ¿Hay un plugin que creció hasta mezclar responsabilidades, o uno con una sola skill que podría
  vivir en otro sin perder nada?
- ¿Los `keywords` y la `description` del `plugin.json` siguen describiendo lo que el plugin
  contiene hoy?

## Paso 6 — Deriva respecto de la referencia y del uso real

- Compara las convenciones que declara `references/plugin-reference.md` con lo que hacen los
  plugins de verdad. Cuando difieren, decide cuál está mal: a veces la referencia quedó vieja, no
  el código.
- Señala componentes documentados pero **nunca usados** (`commands/`, `agents/`, `.mcp.json`,
  `userConfig`): no es un error, pero una convención que nadie ejerce suele estar sin verificar.
- Si el usuario puede aportarlo, pregunta **qué skills usa el equipo realmente**. Una skill que
  nadie invoca en meses es candidata a borrarse o a que su `description` esté fallando.

## Paso 7 — Informe

```markdown
# Auditoría del marketplace

**Estado mecánico:** <✔ validate + conventions OK | ✖ hay que arreglar esto primero>
**Resumen:** <2-4 frases: qué está sólido y dónde está el problema principal.>

## 🔴 Coherencia rota — arreglar
- **<archivo>** — <referencia obsoleta, trigger que compite, criterio que derivó> · *Arreglo:* <acción>

## 🟠 Diseño — vale la pena
- **<plugin/skill>** — <hallazgo> · *Arreglo:* <acción>

## 🟡 Simplificación — se puede quitar
- **<plugin/skill/convención>** — <qué sobra y por qué>

(Omite las secciones vacías.)

## Qué está bien
<1-3 puntos.>

## Propuesta de orden
1. <cambio concreto, empezando por lo que desbloquea o evita más confusión>
2. <...>
```

## Cierre

Recuerda al usuario que cualquier cambio que aplique después requiere **bumpear la `version`** del
plugin afectado (si no, los consumidores no lo reciben) y que CI valida manifiestos y convenciones
en cada PR — pero no puede detectar nada de lo que revisa esta skill, porque son juicios de
diseño, no reglas mecánicas.
