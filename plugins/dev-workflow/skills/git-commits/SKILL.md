---
name: git-commits
description: "Crea mensajes de commit de git siguiendo el estandar de Platanus (tipo(contexto) seguido de descripcion en ingles, imperativo, max 100 caracteres). Usala siempre que el usuario pida hacer un commit, generar un mensaje de commit, subir cambios a git, o cuando haya cambios sin commitear (git status/diff) y se sugiera guardarlos en git. Tambien aplica si el usuario menciona commit, git commit, guardar cambios en git, o pide dividir cambios grandes en varios commits."
---

# Git Commits (estándar Platanus)

Skill para crear commits de git breves, ordenados y descriptivos, siguiendo la
convención de [Platanus](https://la-guia.platan.us/setup/configuracion_de_proyectos/git).

## Formato del mensaje

```
tipo(contexto): descripción
```

- **Todo en inglés.**
- Normalmente **una sola línea**.
- **Máximo 100 caracteres** en la primera línea.

### Tipo

Uno de:

| tipo     | uso                                                              |
|----------|-------------------------------------------------------------------|
| feat     | un nuevo feature                                                   |
| fix      | corrección de un bug                                               |
| docs     | cambios en documentación                                           |
| style    | cambios que no afectan el significado del código (espacios, etc.) |
| refactor | cambio de código que no agrega feature ni corrige bug              |
| perf     | cambios que solo mejoran performance                               |
| test     | agrega o corrige tests                                             |
| chore    | cambios al proceso de build o herramientas auxiliares              |

### Contexto

- Palabra (o frase corta) en `kebab-case` que indica la parte del código o
  funcionalidad afectada. Ej: `user-signup`.
- Opcionalmente se puede agregar el componente específico afectado, separado
  por `/`, usando el mismo formato que tiene en el código (ej. `CamelCase`
  para una clase). Ej: `api/LoginService`.

### Descripción

- Verbo en **imperativo** en inglés: `change`, no `changed` ni `changes`.
- Separada del contexto por un espacio.
- **Sin mayúscula** al inicio.
- **Sin punto** final.

### Ejemplos válidos

```
feat(user-signup): add email verification step
fix(api/LoginService): handle expired token correctly
docs(readme): explain local setup steps
refactor(pudato/search): simplify key-based lookup logic
chore(deps): bump fastapi to 0.115
```

## Flujo de trabajo

1. **Revisar el estado del repo.** Correr `git status` y `git diff` (o
   `git diff --staged` si ya hay staging) para entender qué cambió.
2. **Agrupar los cambios en commits lógicos.** Si hay muchos cambios
   acumulados que tocan cosas distintas (ej. un fix y un feature no
   relacionados, o cambios en módulos distintos), NO los mezcles en un solo
   commit. Sepáralos en varios commits, cada uno con su propio `tipo(contexto)`
   coherente. Usa `git add -p` o `git add <archivos>` específicos para armar
   cada commit por separado en vez de un `git add -A` genérico.
3. **Redactar el/los mensaje(s)** siguiendo el formato de arriba.
4. **Mostrarle al usuario** los commits propuestos (mensaje + qué archivos
   entrarían en cada uno) antes de ejecutar nada.
5. **Esperar aprobación explícita del usuario antes de hacer `git push`.**
   Se puede hacer `git commit` una vez que el usuario aprueba los mensajes,
   pero el `push` a remoto SIEMPRE requiere una confirmación aparte y
   explícita del usuario. Nunca asumas que aprobar el mensaje del commit
   implica aprobar el push.

## Reglas duras (no negociables)

- Nunca escribir el mensaje en español, aunque el resto de la conversación
  sea en español.
- Nunca superar los 100 caracteres en la primera línea.
- Nunca dejar mayúscula inicial ni punto final en la descripción.
- Nunca hacer `git push` sin que el usuario lo apruebe explícitamente,
  incluso si ya aprobó el/los commit(s).
- Si un conjunto de cambios mezcla varios tipos/contextos claramente
  distintos, dividir en varios commits en lugar de forzar un solo mensaje
  genérico.
