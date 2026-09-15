# Despliegue y manejo de dependencias — Backend (DigitalOcean)

Guía de referencia para actualizar el backend en el droplet cada vez que subas
cambios o necesites instalar/actualizar una dependencia de Python.

## Datos del servidor (no cambian, guárdalos aquí para no tener que redescubrirlos)

| Dato | Valor |
|---|---|
| Ruta del proyecto | `/var/proyectos/megahydraulic_fastapi` |
| Entorno virtual (venv) | `/var/proyectos/megahydraulic_fastapi/env` |
| Servicio systemd | `fastapi.service` |
| Archivo del servicio | `/etc/systemd/system/fastapi.service` |
| Usuario que corre el proceso | `www-data` |
| Cómo arranca | `python main.py` (ya no `uvicorn main:app` directo) |
| Puerto | `8000` |
| Python en el droplet | 3.12.7 |

`main.py` decide si arranca con `--reload` o no según la variable de entorno
`APP_ENV`. En el servidor **no** debe existir `APP_ENV=development` en el
`.env` — así arranca siempre en modo producción (sin reload). Esa variable
solo va en tu `.env` local.

---

## 1. Caso más común: subiste cambios de código (sin tocar `requirements.txt`)

```bash
ssh root@<ip-del-droplet>
cd /var/proyectos/megahydraulic_fastapi
git status                    # confirma que no haya cambios locales sin commitear
git pull origin master
sudo systemctl restart fastapi
sudo systemctl status fastapi --no-pager
```

Con eso basta. No hay que tocar el archivo del servicio ni reinstalar nada.

---

## 2. Agregar una dependencia nueva

**En tu máquina local, primero:**

```bash
pip install nombre-del-paquete
pip freeze | grep -i nombre-del-paquete
```

Copia la línea (`nombre-del-paquete==X.Y.Z`) y agrégala a `requirements.txt`
a mano, en orden alfabético (así queda el archivo). Prueba que tu app siga
funcionando local, y luego haz commit + push de `requirements.txt` junto con
el código que la usa.

**En el servidor:**

```bash
cd /var/proyectos/megahydraulic_fastapi
git pull origin master
/var/proyectos/megahydraulic_fastapi/env/bin/pip install -r requirements.txt
sudo systemctl restart fastapi
sudo systemctl status fastapi --no-pager
```

`pip install -r requirements.txt` instala solo lo que falte o no coincida
con la versión pineada — no reinstala todo desde cero.

---

## 3. Actualizar una dependencia existente a una versión más nueva

**En tu máquina local:**

```bash
pip install --upgrade nombre-del-paquete
pip freeze | grep -i nombre-del-paquete
```

Actualiza esa misma línea en `requirements.txt` con la nueva versión. Prueba
localmente (sobre todo si es una librería con lógica de negocio real, como
`reportlab` para los PDFs) antes de subir.

**En el servidor:** exactamente los mismos 4 comandos del punto 2 (`git pull`
→ `pip install -r requirements.txt` → `restart` → `status`).

---

## 4. Actualizar TODAS las dependencias a la última versión

Solo si de verdad lo necesitas (no es rutina). En tu máquina local:

```bash
pip list --outdated
pip install --upgrade nombre1 nombre2 nombre3 ...
pip freeze > requirements.txt
```

⚠️ Revisa el `requirements.txt` generado: `pip freeze` incluye **todo** lo
instalado en tu entorno, incluyendo cosas que no son de este proyecto si tu
venv está "sucio". Compara contra el `requirements.txt` anterior y deja solo
lo que realmente usa la app. Prueba localmente que todo (incluyendo generar
un PDF de cada tipo: mantenimiento, ACESCO y cotización) siga funcionando
antes de subir. Luego, mismos pasos del punto 2 en el servidor.

---

## 5. Si alguna vez hay que tocar el archivo del servicio

Esto casi nunca hace falta (solo si cambia la ruta del proyecto, el usuario,
o la forma de arrancar la app):

```bash
sudo nano /etc/systemd/system/fastapi.service
# editar lo que corresponda
sudo systemctl daemon-reload      # obligatorio después de editar el archivo
sudo systemctl restart fastapi
sudo systemctl status fastapi --no-pager
```

`daemon-reload` es el paso que más se olvida — sin él, systemd sigue usando
la versión vieja del archivo aunque lo hayas guardado.

---

## 6. Verificar que quedó bien

```bash
curl -sf http://localhost:8000/docs && echo "OK"
sudo journalctl -u fastapi -n 50 --no-pager
```

Si `curl` no responde o el log muestra errores/tracebacks apenas arranca,
el problema está casi siempre en: una dependencia que faltó instalar, o un
error de sintaxis/import en el código que se acaba de subir.

---

## 7. Si algo se rompe y necesitas volver atrás

```bash
cd /var/proyectos/megahydraulic_fastapi
git log --oneline -5                  # ubica el commit anterior bueno
git checkout <hash-del-commit-bueno>
/var/proyectos/megahydraulic_fastapi/env/bin/pip install -r requirements.txt
sudo systemctl restart fastapi
```

Cuando confirmes que todo quedó estable otra vez, vuelve a `git checkout
master` para no quedarte en un commit suelto ("detached HEAD"), arregla el
problema con calma, y vuelve a desplegar siguiendo el punto 1 o 2.

---

## Cheat sheet (lo de todos los días)

```bash
ssh root@<ip-del-droplet>
cd /var/proyectos/megahydraulic_fastapi
git pull origin master
/var/proyectos/megahydraulic_fastapi/env/bin/pip install -r requirements.txt   # solo si requirements.txt cambió
sudo systemctl restart fastapi
sudo systemctl status fastapi --no-pager
curl -sf http://localhost:8000/docs && echo OK
```
