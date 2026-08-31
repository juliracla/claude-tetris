---
name: clima-local
description: Consulta el clima actual y el pronóstico de los próximos días desde la terminal, sin API key. Usar cuando el usuario pregunte por el clima, la temperatura, si va a llover, el pronóstico, o el tiempo en su ciudad o en cualquier otra ("¿cómo está el clima?", "¿qué tiempo hace en Bogotá?", "¿llueve mañana?").
---

# Clima local

Obtiene el clima usando `wttr.in` (datos abiertos, sin API key ni registro).
Por defecto detecta la ubicación a partir de la IP pública; también acepta una
ciudad explícita.

## Uso

```bash
# Clima de la ubicación detectada automáticamente
python .claude/skills/clima-local/clima.py

# Clima de una ciudad concreta
python .claude/skills/clima-local/clima.py "Bogotá"
python .claude/skills/clima-local/clima.py "Madrid, ES"

# Con pronóstico de los próximos 3 días
python .claude/skills/clima-local/clima.py --dias 3
python .claude/skills/clima-local/clima.py "Lima" --dias 2

# Salida JSON cruda (para procesar o extraer campos puntuales)
python .claude/skills/clima-local/clima.py --json
```

En Windows usa `python`; si no existe, prueba `py -3` o `python3`.

## Salida

Texto en español: ubicación, condición, temperatura y sensación térmica,
humedad, viento, precipitación y, con `--dias N`, mínima/máxima y probabilidad
de lluvia por día.

## Notas

- Requiere conexión a internet. Si `wttr.in` no responde (timeout de 15 s o
  error HTTP), el script imprime el error y sale con código 1 — repórtalo al
  usuario en vez de inventar datos.
- La ubicación automática viene de la IP, así que con VPN puede ser incorrecta;
  en ese caso pásale la ciudad como argumento.
- Al responder, resume los datos en una o dos líneas en lugar de volcar toda la
  salida, salvo que el usuario pida el detalle.
