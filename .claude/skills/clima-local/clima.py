#!/usr/bin/env python3
"""Clima actual y pronostico usando wttr.in (sin API key)."""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

TIMEOUT = 15
UA = "curl/8"  # wttr.in devuelve JSON limpio con user-agent de tipo curl


def fetch(lugar):
    ruta = urllib.parse.quote(lugar) if lugar else ""
    url = "https://wttr.in/{}?format=j1&lang=es".format(ruta)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def nombre_lugar(data, lugar):
    try:
        a = data["nearest_area"][0]
        partes = [a[k][0]["value"] for k in ("areaName", "region", "country")
                  if a.get(k) and a[k][0].get("value")]
        vistos = []
        for p in partes:
            if p and p not in vistos:
                vistos.append(p)
        if vistos:
            return ", ".join(vistos)
    except (KeyError, IndexError, TypeError):
        pass
    return lugar or "ubicacion detectada"


def descripcion(bloque):
    for clave in ("lang_es", "weatherDesc"):
        val = bloque.get(clave)
        if val:
            return val[0].get("value", "").strip()
    return "s/d"


def imprimir(data, lugar, dias):
    c = data["current_condition"][0]
    print("Ubicacion: {}".format(nombre_lugar(data, lugar)))
    print("Condicion: {}".format(descripcion(c)))
    print("Temperatura: {} C (sensacion {} C)".format(
        c.get("temp_C", "?"), c.get("FeelsLikeC", "?")))
    print("Humedad: {}%".format(c.get("humidity", "?")))
    print("Viento: {} km/h {}".format(
        c.get("windspeedKmph", "?"), c.get("winddir16Point", "")))
    print("Precipitacion: {} mm".format(c.get("precipMM", "?")))
    print("Observado: {}".format(c.get("localObsDateTime", c.get("observation_time", "?"))))

    if dias <= 0:
        return
    print("\nPronostico:")
    for d in data.get("weather", [])[:dias]:
        horas = d.get("hourly", [])
        lluvia = max((int(h.get("chanceofrain", 0)) for h in horas), default=0)
        media = horas[len(horas) // 2] if horas else {}
        print("  {}: min {} C / max {} C - {} - lluvia {}%".format(
            d.get("date", "?"), d.get("mintempC", "?"), d.get("maxtempC", "?"),
            descripcion(media) if media else "s/d", lluvia))


def main():
    p = argparse.ArgumentParser(description="Clima via wttr.in")
    p.add_argument("lugar", nargs="?", default="",
                   help="ciudad o lugar; por defecto se detecta por IP")
    p.add_argument("--dias", type=int, default=0,
                   help="dias de pronostico a mostrar (0-3)")
    p.add_argument("--json", action="store_true", dest="crudo",
                   help="imprime el JSON crudo de wttr.in")
    args = p.parse_args()

    try:
        data = fetch(args.lugar)
    except urllib.error.HTTPError as e:
        print("Error HTTP {} al consultar wttr.in (lugar desconocido?)".format(e.code),
              file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as e:
        print("No se pudo obtener el clima: {}".format(e), file=sys.stderr)
        return 1

    if args.crudo:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    try:
        imprimir(data, args.lugar, max(0, min(args.dias, 3)))
    except (KeyError, IndexError, TypeError) as e:
        print("Respuesta inesperada de wttr.in: {}".format(e), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
