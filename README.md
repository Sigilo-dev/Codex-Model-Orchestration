# Codex Orchestration — Focused (Sol / Terra / Luna / Astra)

Adaptación **mínima e independiente** de la idea de enrutamiento de roles de
[Cjbuilds/Codex-Orchestration](https://github.com/Cjbuilds/Codex-Orchestration).
No es un clon completo del repositorio original; consulta `docs/ORIGIN.md`.

## Configuración fija

| Trabajo | Modelo | Razonamiento | Agente |
|---|---|---|---|
| Codificación, pruebas, integración y pensamiento rutinario | GPT-6.1 Sol (`gpt-6.1-sol`) | Extra High (`xhigh`) | Root / `code_executor` |
| Decisiones de arquitectura o planificación críticas solamente | GPT-6 Astra (`gpt-6-astra`) | Extra High (`xhigh`) | `critical_planner` |
| Criterios visuales, UI/UX, layout, responsive, revisión visual | GPT-6.1 Terra (`gpt-6.1-terra`) | High (`high`) | `visual_designer` |
| README, ADR, API docs, manuales, documentación | GPT-6 Luna (`gpt-6-luna`) | Extra High (`xhigh`) | `technical_writer` |

**Regla central:** no gastar una invocación a Astra en tareas menores. Sol
resuelve esas decisiones por sí mismo. Terra define la experiencia visual y
Sol implementa el código, incluido HTML/CSS y componentes web.

## Instalar en un proyecto (recomendado)

Requisitos: Python 3.11+ y Codex reciente (Terra necesita Codex CLI 0.159.0+
cuando se utiliza desde CLI). Extrae el ZIP y desde la carpeta extraída ejecuta:

```powershell
python scripts/install.py --scope project --target "C:\ruta\a\tu-proyecto" --dry-run
python scripts/install.py --scope project --target "C:\ruta\a\tu-proyecto"
```

El instalador copia la skill y los cuatro agentes. Si el proyecto **no tiene**
`.codex/config.toml`, instala los valores Sol xhigh como root y activa subagentes.
Si ya existe, lo deja intacto y avisa: verifica que tu configuración tenga el
modelo root y `[agents] enabled = true`. Añade a `AGENTS.md` una política
acotada con marcadores para respetar instrucciones previas. Ante una colisión
con un agente o skill existente se detiene; puedes usar `--force` si deseas
sustituir ese archivo (se guarda una copia `.bak`).

Para usarlo en **todos** tus proyectos:

```powershell
python scripts/install.py --scope user --dry-run
python scripts/install.py --scope user
```

En modo personal usa `~/.agents/skills/sol-router`, `~/.codex/agents`,
`~/.codex/config.toml` y `~/.codex/AGENTS.md`. No toca autenticación ni llaves.
Reinicia Codex tras instalar y comienza una nueva tarea.

## Uso

Solicita cualquier tarea de ingeniería. `AGENTS.md` dirige a Codex a la skill.
También puedes seleccionar explícitamente `$sol-router` cuando sea visible en
`/skills`:

```text
$sol-router Implementa un dashboard responsive con filtros y tests.
$sol-router Diseña una migración segura entre dos arquitecturas.
$sol-router Documenta las rutas API que acabamos de implementar.
```

Es correcto que un bug puntual use únicamente Sol y que una arquitectura
nueva llame a Astra, luego a Terra si es visual, a Sol para código, y a Luna
si debe documentarse. La delegación es condicional, no una cadena obligatoria.

## Inspección y pruebas

```powershell
python scripts/validate.py
python -m unittest discover -s tests -v
codex --version
```

Las pruebas verifican la estructura y reglas locales, **no** hacen llamadas
remotas a los modelos. El entorno Codex debe tener acceso a los cuatro IDs y
sus niveles de razonamiento. No se produce sustitución silenciosa si faltan.

Si ya hay un `AGENTS.md` o `.codex/config.toml`, revisa conflictos de política:
el instalador conserva configuraciones existentes; un root seleccionado en la
interfaz podría diferir de Sol. Para forzar Sol al iniciar desde CLI:

```powershell
codex -m gpt-6.1-sol -c model_reasoning_effort=xhigh
```

## Fuentes de configuración

- [Native Codex subagents](https://developers.openai.com/codex/subagents)
- [Codex skills](https://developers.openai.com/codex/skills)
- [OpenAI model catalog](https://learn.chatgpt.com/docs/models)
- [Repositorio original](https://github.com/Cjbuilds/Codex-Orchestration)

## Licencia

MIT. La licencia y atribución del proyecto de referencia se conservan.
