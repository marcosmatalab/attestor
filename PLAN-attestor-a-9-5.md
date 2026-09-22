# PLAN attestor a 9,5

**Punto de partida:** el repo tal como está hoy. Clon limpio de `main`, HEAD `23370f2e73a4c7d82c90e6bcafd1b146697fea18`. **Nada del plan anterior está aplicado.**
**Fecha de medición:** 22 de septiembre de 2026. Todo lo marcado [MEDIDO] lo ejecuté ese día sobre ese HEAD.
**Nota hoy:** 5,5 sobre 10.
**Objetivo:** 9,5 sobre 10.
**Total:** 16,5 h en 6 fases.

**Por qué la nota de partida baja de 6,0 a 5,5.** El plan anterior puntuaba 7 dimensiones. Este añade una octava, **vigencia del dominio**, que hoy está en 3,0 porque el repo afirma en su sección más sensible algo que dejó de ser cierto el 27 de julio de 2026. No es que el repo haya empeorado: es que la vara antes no miraba ahí.

---

## 0. Cómo usar este documento

Autocontenido. No hace falta volver a ninguna conversación. Cada cifra lleva al lado el comando que la produce.

**Reparto de trabajo, según la regla del 22 de septiembre:**

- **[CC]** lo ejecuta Claude Code, que es el único que toca el árbol. Tú no lanzas comandos en el repo mientras él trabaja.
- **[TÚ]** lo ejecutas tú, porque Claude Code no puede: `git push`, `gh`, credenciales, ajustes de GitHub en el navegador, capturas de pantalla.

Cada fase termina con un bloque **"te devuelvo el control"**: la lista exacta de comandos tuyos, sin huecos que rellenar. Hasta que ese bloque no aparezca, no toques nada.

**Cómo lanzarlo:** una fase por sesión. `lee PLAN-attestor-a-9-5.md y ejecuta la fase 0 entera`. No pases a la siguiente sin que el criterio de terminado esté en verde. El criterio siempre es un comando y su salida esperada, nunca una opinión.

**Orden y por qué ese orden.** La fase 0 va primera porque todas las demás pulen texto, y pulir un texto que afirma algo falso es trabajo que hay que rehacer. La fase 5 va última porque publica hacia fuera, y publicar algo que todavía miente es peor que no publicar.

**Convención:** **[MEDIDO]** lo ejecuté yo el 22 de septiembre sobre este HEAD. **[ESPERADO]** es la salida que debe dar el comando después del cambio, y no lo ejecuté porque el cambio aún no existe. Lo digo cada vez.

---

## 1. Qué cambia respecto al plan de 9,0

| | Plan de 9,0 | Este plan |
|---|---|---|
| Fase 0, vigencia regulatoria | No existe. El Omnibus está en "lo que esto no arregla", como "20 minutos de revisión" | **Fase 0 completa, 3,5 h.** Es la fase que más nota mueve y la que da el titular del repo |
| mypy en modo strict | Incógnita declarada: "puede irse a 4 h" | **Medido: 31 errores en 8 ficheros, ninguno estructural. 1,5 h** |
| Checksums anclados | No aparece | **Fichero de checksums fijados y test que los comprueba.** Hoy ningún test ancla un valor |
| Snapshot de la demo | Se commitea sin puerta que lo valide | Solo se commitea con su test, o no se commitea |
| Señal de vida | Declarada como no comprable con horas | **Workflow programado semanal** que ejecuta el guion de aceptación. Vida real y visible, sin commits de relleno |
| Fase 3 | 4,0 h, la más cara | 3,0 h, porque la incógnita ya está medida |
| Fase 5 | Pages, release y tag, 2,75 h | Lo mismo más el workflow semanal, y el snapshot solo con test |
| Total | 14,0 h para 9,0 | 16,5 h para 9,5 |

---

## 2. El hecho nuevo, y por qué lo cambia todo

El Digital Omnibus sobre IA **ya es derecho vigente**:

- El Consejo le dio luz verde definitiva el **29 de junio de 2026**.
- Se publicó en el DOUE como **Reglamento (UE) 2026/1744**.
- **Entró en vigor el 27 de julio de 2026.**
- Calendario resultante: alto riesgo autónomo del Anexo III a **2 dic 2027**, alto riesgo embebido en productos del Anexo I a **2 ago 2028**, prohibición de NCII y CSAM a **2 dic 2026**, sandboxes regulatorios aplazados a **2 ago 2027**, y el periodo de gracia de transparencia recortado de 6 a 3 meses, con fecha **2 dic 2026**.

Fuentes al final del documento.

### La mala noticia

Hoy el repo dice, literalmente:

- `README.md:506-511`: "As of 23 June 2026 the European Parliament has approved it, but the Council's formal adoption is still pending (expected 29 Jun 2026)... The binding legal text remains Reg. (EU) 2024/1689 (2 Aug 2026 timeline)".
- `src/attestor/classifier/rules/omnibus-2026.yaml:24-30`, el `meta.status_note`, que es la única fuente de verdad del caveat y viaja hasta el PDF del Anexo IV y hasta la interfaz: "Provisional, not yet in force (as of 2026-06-23)... Until then the binding timeline remains the legal-text scenario".
- `meta.status: "pending-formal-adoption"`.
- `web/lib/i18n/dictionaries.ts:70` y `:181`, en inglés y en castellano: "The binding legal text remains Reg. (EU) 2024/1689. The Omnibus column is provisional".
- `tests/test_timeline.py:80`: `assert "provisional" in comparison.omnibus_status.lower()`. Hay un test que **exige** que el repo siga diciéndolo.

Eso lleva **casi dos meses siendo falso**, y es la afirmación más sensible del proyecto. Quien conozca el expediente lo ve en treinta segundos.

### La buena, que es enorme

Los cuatro deltas que modelaste en junio **acertaron**, comparados con el texto adoptado:

| Delta modelado en `omnibus-2026.yaml` | Texto adoptado |
|---|---|
| Anexo III alto riesgo a `2027-12-02` | 2 dic 2027, correcto |
| Anexo I embebido a `2028-08-02` | 2 ago 2028, correcto |
| Art. 50(2), corte de marcado nuevo / heredado a `2026-12-02` | 2 dic 2026, correcto |
| Art. 5, prohibición nueva NCII y CSAM a `2026-12-02` con puerto seguro | dic 2026, correcto |

Y como las fechas viven **en la obligación** y no como fecha global del bundle, absorber la adopción real **no obliga a reescribir ni un vector golden**. El `git diff` de la fase 0 es la prueba, y la puerta de CI que se añade en la fase 3 la convierte en contrato permanente.

Esa es la frase con la que se vende este repo en una entrevista:

> Modelé el Omnibus cuando todavía era una propuesta provisional. Cuando se adoptó de verdad en julio, mi motor lo absorbió añadiendo un bundle nuevo, sin editar un solo byte de los anteriores y sin tocar un solo vector golden. Hay un test que lo impide.

Eso no es compliance, es diseño de datos que aguanta un cambio del mundo real.

---

## 3. Estado medido hoy

Todo ejecutado el 22 de septiembre sobre el HEAD indicado, con Python 3.12.3.

| Qué | Cifra | Comando |
|---|---|---|
| Suite Python | **228 passed** | `pytest` |
| Cobertura | **97 %**, 1085 statements, 35 missed | `pytest --cov=src/attestor` |
| Código muerto | **cero hallazgos** | `vulture src tests --min-confidence 80` |
| Lint | **All checks passed!** | `ruff check .` |
| Formato con ruff 0.8.6 | **exit 0**, 66 ficheros | `ruff format --check .` |
| Formato con ruff 0.16.8 | **exit 1**, 1 fichero: `README.md` | `ruff format --check .` |
| Formato solo sobre código | **exit 0** | `ruff format --check src tests` |
| **mypy strict** | **31 errores en 8 ficheros** | `mypy --strict src/attestor` |
| Frontend | eslint exit 0, build Next 16.2.9 con 3 rutas estáticas, **20 tests vitest** | `npm ci && npm run lint && npm run build && npm test` |
| Ledger, camino feliz | `ledger VERIFIED`, **exit 0** | generado con el snippet del README y `python -m attestor.ledger` |
| Ledger, un byte alterado | `ledger TAMPERED`, **exit 1** | idem |
| Historial | **82 commits, 22 a 25 jun 2026**, 0 trailers de co-autoría | `git log` |
| Ramas remotas | **7**, de las cuales 6 mergeadas | `git branch -r` |
| README | **531 líneas** | `wc -l README.md` |

### Los 31 errores de mypy, desglosados [MEDIDO]

Esta era la única incógnita del plan anterior. Ya no lo es.

| Grupo | Cuántos | Arreglo | Tiempo |
|---|---|---|---|
| Stubs que faltan: `reportlab` (6) y `c2pa` (1) | 7 | `types-reportlab` en dev, y `[[tool.mypy.overrides]]` con `ignore_missing_imports` para `c2pa` | 15 min |
| Re-exports no explícitos en `src/attestor/provenance/__init__.py:12` | 4 | `__all__` en `verifier.py`, o `import X as X` | 10 min |
| `Returning Any` en `ledger/timestamp.py:45` y `provenance/signer.py:81` | 2 | anotar el retorno de la librería y envolver en `bytes(...)` | 10 min |
| Falsos positivos de flujo en `ledger/verifier.py:37` y `:41` | 2 | comprobar `signed_root.timestamp is not None` en vez de la variable `has_timestamp` | 15 min |
| `arg-type` en `api/routes.py:151`: pasas `str` donde el modelo espera el enum | 2 | usar `Role.provider` y `AnnexIIIArea.employment` | 10 min |
| Anotaciones y genéricos sin parametrizar en `annexiv/pdf.py` (líneas 50, 103, 105) | 4 | anotar | 20 min |
| Resto | 10 | del mismo tipo que los anteriores | 20 min |

**Presupuesto real: 1,5 h.** El único con contenido de fondo es el de `routes.py:151`: pydantic coacciona el `str` en tiempo de ejecución y funciona, pero es el sitio donde el tipado dice algo verdadero.

### Los hashes de hoy, que hay que preservar [MEDIDO]

Estos cuatro valores son la referencia de todo el plan. Si alguno cambia sin que una fase lo diga, algo se rompió.

```
bundle v2026-08      sha256 = 7e77bc0715a2b5836f83e6c50e69ab312ca8b7167c1c747674d8143a3312d49d
bundle omnibus-2026  sha256 = a52cb5e185c01fa0cf62b967a659d5cc8e7769b176e25b3eb2e9647299462c51

classify(provider, employment) bajo v2026-08     = 15815cd8f577dea7cc09696acc9a3e96870664573ea428e7c81bb8b06a84bd17
classify(provider, employment) bajo omnibus-2026 = 3bc20cb8a68d47c16d36c91a400acd2e0b03eb2020f2983a14bdfc7a56fe24f0
classify(deployer público, employment) bajo v2026-08     = da42d3cb8723005638fc430e8b0c13f36ed390e48d1fc63a07ea075afe2bb754
classify(deployer público, employment) bajo omnibus-2026 = a3cc87ff4829ebbcbec63a3dc074948db7e57a73b25394c1eae808451d0bc546
```

El primero de la lista de clasificaciones, `15815cd8...`, es el que se lee dentro de `docs/dashboard.png`. Es el activo más valioso del repo y el plan lo protege.

### El experimento que decide la fase 0 [MEDIDO]

Cambié **una sola línea** del `meta` de cada bundle y volví a calcular:

| Qué toqué | `sha256` del bundle | Checksum de clasificación |
|---|---|---|
| Nada | `a52cb5e1...` (omnibus) | `3bc20cb8...` |
| `meta.status_note` de `omnibus-2026` | pasa a `e2a81819...` | pasa a `6632908b...` |
| `meta.description` de `v2026-08` | pasa a `a9512f9d...` | **`15815cd8...` pasa a `9f4f6a80...`** |

Conclusión medida: **editar el `meta` de un bundle invalida todos los checksums derivados de él, y editar `v2026-08` invalida la captura del README.** Por eso la fase 0 no edita ningún bundle. Ver ADR 1.

---

## 4. Decisiones de diseño

### 4.1 Los bundles son inmutables: el cambio regulatorio se absorbe creando uno nuevo

**Decisión.** No se edita ni un byte de `v2026-08.yaml` ni de `omnibus-2026.yaml`. Se crea `src/attestor/classifier/rules/reg-2026-1744.yaml`, copia del bundle Omnibus con un `meta` nuevo que declara la vigencia real. Los dos anteriores quedan congelados como artefactos históricos.

**Por qué.** El repo ancla hashes de bundle en el ledger. Reescribir a posteriori un artefacto cuyo hash ya está anclado es exactamente lo que un sistema de evidencia no debe hacer, y el docstring de `bundle.py:4` ya lo dice: "F2 will add a Digital Omnibus scenario as a separate bundle file, never a migration of this one". La coherencia es el argumento, no la comodidad.

**Alternativa descartada.** Editar el `meta` de `omnibus-2026` para poner que ya está en vigor. Descartada porque cambia su `sha256` de `a52cb5e1...` a `e2a81819...` [MEDIDO], rompe los checksums de todo lo clasificado bajo él, y sobre todo porque destruye el mejor argumento del proyecto: que el bundle provisional de junio sigue ahí, intacto, y se puede comparar con el vigente.

**Trade-off.** El árbol pasa a tener tres bundles, dos de ellos históricos, y hay que explicar en el README qué es cada uno. Se acepta: esa explicación **es** la historia que vende el repo.

### 4.2 El bundle por defecto pasa a ser el vigente, y la captura se regenera

**Decisión.** `DEFAULT_VERSION` en `src/attestor/classifier/bundle.py:19` pasa de `"v2026-08"` a `"reg-2026-1744"`, y la constante `LEGAL_TEXT_BUNDLE` que usa `src/attestor/api/routes.py:50` hace lo propio. La captura `docs/dashboard.png` se regenera porque el checksum del demo cambia.

**Por qué.** Un motor de cumplimiento cuyo comportamiento por defecto aplica un calendario derogado está mal, y esa es la primera pregunta que hace alguien que conozca el expediente. Ningún adorno del README compensa eso.

**Alternativa descartada.** Dejar el defecto en `v2026-08` para conservar `15815cd8...` y no tocar la captura. Descartada: ahorra media hora y deja un defecto incorrecto en el sitio donde más se nota.

**Trade-off y su coste medido.** Hay 12 puntos de test que llaman a `load_bundle()` sin argumento (`test_bundle_integrity.py` en 6 sitios, `test_checksum_isolation.py` en 2, `test_classifier_determinism.py` en 2, y 2 más) y que aseveran cosas de `v2026-08`. Pasan a `load_bundle("v2026-08")` explícito, que además es mejor estilo. Media hora de sed cuidadoso, y el resultado es que ningún test depende de cuál sea el defecto.

### 4.3 El caveat de provisionalidad no se borra: se convierte en histórico

**Decisión.** `meta.status_note` sigue siendo la única fuente de verdad del texto que viaja al PDF y a la interfaz, pero ahora hay dos notas distintas: la del bundle vigente dice que está en vigor desde el 27 jul 2026, y la del bundle `omnibus-2026` se queda **exactamente como está**, describiendo la situación del 23 de junio.

**Por qué.** El mecanismo ya es correcto: `timeline.py:96` y `annexiv/generator.py:83` leen el caveat del bundle, nunca lo hardcodean. Lo que estaba mal era el dato, no el diseño. Cambiar el diseño ahora sería tirar la parte buena.

**Alternativa descartada.** Meter la vigencia en el código, por ejemplo una función `is_in_force()`. Descartada porque devuelve al repo al pecado que evitó desde el principio: interpretación normativa fuera del bundle.

### 4.4 Lo que no se toca

- **Nada de lógica del motor.** Ni reglas, ni canonicalización, ni Merkle, ni firma. Cobertura del 97 % y vectores golden que la fijan: cambiar ahí es riesgo puro sin retorno.
- **Ningún golden existente se modifica.** Su no modificación es la prueba de la fase 0, y la fase 3 la convierte en puerta.
- **No se amplía el alcance regulatorio.** Nada de Art. 6(3), nada de Arts 18/19/20, nada de sandboxes. Esa sección de simplificaciones conocidas del README es honesta y ya suma.
- **No se reescribe el historial.** Los 82 commits de junio se declaran en la fase 4.
- **No se implementa KMS.** Se declara la costura, ver ADR 3.

---

## 5. Las fases

### Fase 0: Vigencia regulatoria

**Objetivo:** que el motor aplique por defecto el derecho vigente, que ninguna afirmación del repo sobre el estado del Omnibus sea falsa, y que el `git diff` demuestre que absorberlo no tocó ni un vector golden.

**Pasos [CC]:**

1. Rama: `git checkout -b feat/reg-2026-1744`

2. Crear `src/attestor/classifier/rules/reg-2026-1744.yaml` copiando `omnibus-2026.yaml` **entero**, y cambiando **solo el bloque `meta` y el comentario de cabecera**. El `meta` nuevo:
   ```yaml
   meta:
     version: "reg-2026-1744"
     regulation: "EU AI Act (Reg. (EU) 2024/1689) as amended by Reg. (EU) 2026/1744 (Digital Omnibus on AI)"
     scenario: "in-force"
     status: "in-force"
     in_force_since: "2026-07-27"
     status_note: >-
       In force. Regulation (EU) 2026/1744 (Digital Omnibus on AI) was adopted by
       the Council on 2026-06-29, published in the Official Journal, and entered
       into force on 2026-07-27. This bundle is the binding timeline today.
       Bundle v2026-08 (Reg. (EU) 2024/1689 as originally enacted) and bundle
       omnibus-2026 (the Omnibus as modelled on 2026-06-23, while still a
       proposal) are kept frozen as historical artifacts: their bytes, their
       sha256 and their golden vectors are unchanged by this addition.
     description: >-
       Binding timeline as of 2026-07-27: Annex III high-risk 2027-12-02, Annex I
       embedded 2028-08-02, the Art. 50(2) new/legacy marking split, and the
       Art. 5 NCII/CSAM prohibition (2026-12-02, with a safe harbour).
   ```
   Las reglas, obligaciones, artículos y fechas se copian **sin tocar una coma**: ya son las correctas.

3. `src/attestor/classifier/bundle.py:19`: `DEFAULT_VERSION = "reg-2026-1744"`.

4. `src/attestor/classifier/timeline.py:20-22`: `BINDING_SCENARIO = "in-force"`, añadir `IN_FORCE_VERSION = "reg-2026-1744"`, conservar `LEGAL_TEXT_VERSION` y `OMNIBUS_VERSION` como están. `compare_timelines` pasa a comparar **texto original contra vigente**: el segundo bundle por defecto es `IN_FORCE_VERSION`. El campo `omnibus_status` del modelo se conserva con ese nombre para no romper la API ni el frontend, y su docstring pasa a decir que es la nota de estado del bundle vigente. Actualizar el docstring del módulo, que hoy dice "the provisional Omnibus bundle".

5. `src/attestor/api/routes.py:50`: la constante de bundle pasa al vigente. Revisar `routes.py:151` de paso: usa `Role.provider` y el enum de área en vez de cadenas, que es uno de los errores de mypy y se arregla gratis aquí.

6. `src/attestor/classifier/model.py:108`: el comentario "Digital Omnibus addition to Art. 5 (provisional, not yet in force)" pasa a citar el Reglamento 2026/1744 y su fecha de entrada en vigor.

7. Crear `tests/golden/reg-2026-1744.yaml`: copia literal de `tests/golden/omnibus-2026.yaml` con la cabecera adaptada. Las fechas esperadas son idénticas, y ese es justamente el punto.

8. Crear `tests/test_regulatory_evolution.py`, que es **la pieza que más vale de toda la fase**. Cuatro aserciones:
   - el bundle vigente carga, `meta.status == "in-force"`, y `meta.in_force_since == "2026-07-27"`;
   - `load_bundle("v2026-08").sha256 == "7e77bc07...49d"` y `load_bundle("omnibus-2026").sha256 == "a52cb5e1...c51"`, los valores exactos de la sección 3, o sea que **añadir el bundle vigente no alteró ni un byte de los históricos**;
   - para cada vector del golden de `omnibus-2026`, las fechas del bundle vigente coinciden una a una;
   - el `status_note` del bundle histórico `omnibus-2026` sigue conteniendo "provisional", porque describe una situación que fue real.

9. Actualizar los tests que hoy exigen que el repo mienta:
   - `tests/test_timeline.py:76-80`: la aserción pasa a comprobar que `omnibus_status` es el `status_note` del bundle **vigente** y que contiene "in force". El test de que el caveat se lee del bundle y no está hardcodeado se conserva, que es lo valioso.
   - `tests/test_bundle_integrity.py:76`: renombrar a `test_historical_omnibus_bundle_keeps_its_provisional_status` y dejar sus aserciones intactas. Añadir un test hermano para el bundle vigente.
   - `tests/test_annexiv_generator.py:69-75`: el dossier bajo el bundle vigente lleva nota de estado sin la palabra "provisional". El caso del bundle histórico se conserva.
   - Los 12 `load_bundle()` sin argumento pasan a `load_bundle("v2026-08")` explícito, según 4.2.

10. Frontend, todo en `web/`:
    - `lib/i18n/dictionaries.ts:70` (inglés) y `:181` (castellano): el texto pasa a decir que la columna de la derecha es el derecho vigente desde el 27 jul 2026, y la de la izquierda el texto original. Se conservan las dos fechas siempre, que es la regla de honestidad del proyecto.
    - `:73` y `:184`: `thOmnibus` pasa de "Omnibus (provisional)" a "In force (Reg. 2026/1744)" y su equivalente en castellano.
    - `components/TimelineTable.tsx:10`: el literal de respaldo `"pending formal adoption"` pasa a `"in force"`.
    - `components/__tests__/fixtures.ts:52` y `TimelineTable.test.tsx:14-16`: la cadena esperada acompaña al cambio.

11. `README.md`: la fila F2 (`:124`) y el bloque de honestidad (`:506-511`) pasan a decir la verdad de hoy. Texto literal propuesto para el bloque de honestidad:
    > **The Digital Omnibus is in force.** Regulation (EU) 2026/1744 was adopted by the Council on 29 June 2026 and entered into force on 27 July 2026, amending Reg. (EU) 2024/1689: Annex III high-risk moves to 2 Dec 2027, Annex I embedded to 2 Aug 2028. Attestor still shows **both** timelines, because knowing what changed is part of the answer: bundle `v2026-08` is the Regulation as originally enacted, and bundle `reg-2026-1744` is the binding timeline today. The bundle `omnibus-2026`, modelled on 23 June 2026 while the Omnibus was still a proposal, is kept frozen: its four deltas matched the adopted text, and absorbing the adoption required no change to a single golden vector.

12. Añadir `docs/regulatory-changelog.md`, unas 30 líneas: qué bundle representa qué, con las fechas de cada hito (16 jun aprobación del Parlamento, 29 jun adopción del Consejo, 27 jul entrada en vigor) y los `sha256` de cada bundle. Es el documento que demuestra que sabes versionar derecho, no solo código.

**Criterio de terminado [CC]:**
```bash
pytest
# [ESPERADO] todo pasa, unos 233 tests (228 de hoy más los de evolución regulatoria)

python -c "from attestor.classifier import load_bundle as L; print(L('v2026-08').sha256)"
# [ESPERADO] 7e77bc0715a2b5836f83e6c50e69ab312ca8b7167c1c747674d8143a3312d49d
python -c "from attestor.classifier import load_bundle as L; print(L('omnibus-2026').sha256)"
# [ESPERADO] a52cb5e185c01fa0cf62b967a659d5cc8e7769b176e25b3eb2e9647299462c51
# Los dos [MEDIDO] hoy: si cambian, se editó un bundle histórico y hay que revertir

git diff --stat main -- tests/golden/v2026-08.yaml tests/golden/omnibus-2026.yaml \
  src/attestor/classifier/rules/v2026-08.yaml src/attestor/classifier/rules/omnibus-2026.yaml
# [ESPERADO] salida vacía. Es LA prueba de la fase

grep -rn "pending formal adoption\|not yet in force\|still pending" README.md src/ web/lib web/components
# [ESPERADO] cero aciertos fuera del bundle histórico omnibus-2026.yaml y de su test

cd web && npm test && cd ..
# [ESPERADO] 20 passed
```

**Te devuelvo el control [TÚ]:**
```bash
git push -u origin feat/reg-2026-1744
gh pr create --fill
gh pr merge --merge
```
Y una cosa a mano, media hora: **regenerar `docs/dashboard.png`**. Levanta backend y frontend como dice el README, abre `http://localhost:3000/demo`, ejecuta el demo y guarda la captura. El checksum que saldrá ya no es `15815cd8...` porque ahora el demo clasifica bajo el bundle vigente. Anótalo: lo necesitas para la fase 2 y para la tabla de afirmaciones de la fase 4.

**Horas: 3,5.**
**Nota al cerrar: 7,0.** Vigencia del dominio sube de 3,0 a 9,5, y el examen hostil de 4,0 a 6,0.

---

### Fase 1: La verdad

**Objetivo:** que ninguna afirmación del repo se desmonte con un `grep`, y que el CI no pueda envejecer solo.

**Pasos [CC]:**

1. Rama: `git checkout -b fix/claims-and-ci`

2. **KMS.** `README.md:126`, fila F4, texto exacto nuevo:
   `| **F4** | C2PA signer: X.509 manifest + optional RFC3161 timestamp. Keys are config-driven and sign inside a \`Signer.from_callback\` seam, the same interface a KMS/HSM signer plugs into. No KMS backend is implemented. | ✅ |`
   `README.md:487`, fila de la tabla Stack:
   `| C2PA keys | Local PEM chain + key, read from config. \`Signer.from_callback\` is the seam a KMS/HSM signer would plug into; no KMS backend ships here |`
   `src/attestor/config.py` líneas 4, 22 y 31: los comentarios pasan de "in production the key lives in a KMS/HSM" a "the key path is config-driven; a KMS/HSM signer would replace the loader". Igual en `src/attestor/ledger/keys.py:8`.
   Fundamento [MEDIDO]: `git grep -rniE "kms|hsm|boto3|aws"` da 20 aciertos y **ninguno es código**. No hay `boto3` en `pyproject.toml`.

3. **LLM.** `README.md:486` se sustituye por:
   `| Annex IV | Deterministic template derived from the classification, no LLM. Citations validated against the bundle |`
   Fundamento [MEDIDO]: no hay ninguna dependencia de LLM en `pyproject.toml` ni en `web/package.json`, y `src/attestor/annexiv/generator.py:3` empieza diciendo "No LLM". La fila contradecía `README.md:8` y `:16`, que son la tesis del repo.

4. **Variables fantasma en `.env.example`.** Borrar las líneas 8 y 9 (`DATABASE_URL` y su comentario), y las 16 y 17 (`AWS_REGION`, `C2PA_SIGNING_KEY_ARN`). Reescribir la línea 13, que hoy promete KMS. Quedan solo las seis que `src/attestor/config.py` lee de verdad: `APP_ENV`, `LOG_LEVEL`, `C2PA_CERT_PATH`, `C2PA_PRIVATE_KEY_PATH`, `RFC3161_TSA_URL`, `LEDGER_SIGNING_KEY_PATH`.
   Fundamento [MEDIDO]: ninguna de las tres aparece en `src/`, y `Settings` con `extra="ignore"` se las traga en silencio.

5. **Pinar las herramientas.** En `pyproject.toml`: línea 43 a `"pytest==9.1.1"`, 44 a `"httpx==0.28.1"`, 45 a `"ruff==0.16.8"`. Luego `pip install -e ".[dev]"` y `ruff format .`. El diff debe tocar **solo `README.md`**: [MEDIDO] `ruff format --check src tests` ya da exit 0 hoy con ruff 0.16.8.
   Fundamento [MEDIDO]: con ruff 0.8.6 la puerta da exit 0 y con 0.16.8 da exit 1, y nadie tocó el repo. Ruff 0.16 empezó a formatear bloques de Python dentro de Markdown.

6. **Actions pinadas.** En `.github/workflows/ci.yml`, cambiar `actions/checkout@v4`, `actions/setup-python@v5` y `actions/setup-node@v4` por sus SHA completos. El plan anterior pinaba las dependencias de Python y dejaba las actions flotando, que es el mismo problema por otra puerta. Añadir `cache: pip` al `setup-python`.

7. Quitar `pyproject.toml:26`, la línea `"Private :: Do Not Upload",`. No publica nada: solo deja de decirle al revisor que el paquete no está pensado para usarse.

**Criterio de terminado [CC]:**
```bash
ruff check . && ruff format --check . && pytest && echo OK
# [ESPERADO] All checks passed! / 69 files already formatted / ~233 passed / OK

git grep -niE "kms|hsm|aws" -- README.md .env.example src/
# [ESPERADO] solo líneas que describan la costura from_callback

grep -n "LLM" README.md
# [ESPERADO] solo líneas que nieguen el uso de LLM
```

**Te devuelvo el control [TÚ]:**
```bash
git push -u origin fix/claims-and-ci
gh pr create --fill && gh pr merge --merge
# y las 6 ramas mergeadas, comprobadas una a una con ahead=0:
git push origin --delete docs/dashboard-screenshot docs/readme-hook docs/readme-polish \
  feat/web-i18n feature/f8-dashboard feature/frontend-redesign
```

**Horas: 1,5.**
**Nota al cerrar: 7,6.** Examen hostil de 6,0 a 8,0, higiene resuelta.

---

### Fase 2: Reproducibilidad

**Objetivo:** que un tercero verifique el ledger y reproduzca un checksum desde el clon, sin escribir una línea de Python.

Hoy eso no se puede. [MEDIDO] el comando literal del `README.md:359`:
```
$ python -m attestor.ledger out/ledger
could not load ledger from out/ledger: [Errno 2] No such file or directory: 'out/ledger/records.json'
$ echo $?
2
```
La maquinaria sí funciona: generé un ledger a mano con el snippet del propio README y verificó con exit 0, y alterándole un byte dio `TAMPERED` con exit 1. Lo que no existe es el camino del revisor.

**Pasos [CC]:**

1. Rama: `git checkout -b feat/example-ledger-and-cli`

2. Crear `scripts/make_example_ledger.py`: genera una clave en un temporal, crea un `Ledger()`, hace `append` de tres registros con hashes fijos (uno de clasificación con el checksum del bundle vigente, uno de dossier, uno de C2PA), `seal(key)` y `save_ledger("examples/ledger", ...)`. La clave privada **nunca** se commitea.

3. Ejecutarlo y commitear `examples/ledger/records.json` y `examples/ledger/signed_root.json`. Son deterministas: Ed25519 es RFC 8032 y el Merkle es RFC 6962.

4. `examples/ledger/README.md`, 15 líneas: qué son los dos ficheros, con qué clave se firmaron, y que la privada no está ni estará.

5. Crear `src/attestor/cli.py` con `main()` y tres subcomandos sobre lo que ya existe:
   - `attestor classify --role provider --annex-iii-area employment [--bundle VERSION] [--checksum-only]`. El `--bundle` importa: con él, la tabla de afirmaciones de la fase 4 puede enseñar los dos escenarios.
   - `attestor ledger verify <dir>`, reusando `src/attestor/ledger/__main__.py` y conservando sus códigos de salida: 0 verificado, 1 manipulado, 2 error de uso.
   - `attestor demo`, el mismo camino que `POST /api/demo/run`.

6. `pyproject.toml`: añadir
   ```toml
   [project.scripts]
   attestor = "attestor.cli:main"
   ```

7. Mejorar el mensaje de uso de `src/attestor/ledger/__main__.py` para que mencione `examples/ledger`.

8. Crear `tests/test_cli.py` (los tres subcomandos y sus códigos de salida) y `tests/test_example_ledger.py` (el directorio commiteado verifica, y alterar un byte da exit 1).

9. `README.md:357-362`: el bloque del verificador apunta a `examples/ledger`, que ya existe, en vez de a `out/ledger`, que no existió nunca.

**Criterio de terminado [CC]:**
```bash
pip install -e .

attestor ledger verify examples/ledger
# [ESPERADO] ledger VERIFIED (Merkle root intact, Ed25519 signature valid); no timestamp
echo $?   # [ESPERADO] 0

sed -i 's/sys-1/sys-9/' examples/ledger/records.json
attestor ledger verify examples/ledger
# [ESPERADO] ledger TAMPERED - integrity_ok=False, signature_ok=True
echo $?   # [ESPERADO] 1
git checkout examples/ledger/records.json

attestor classify --role provider --annex-iii-area employment --bundle v2026-08 --checksum-only
# [ESPERADO] 15815cd8f577dea7cc09696acc9a3e96870664573ea428e7c81bb8b06a84bd17   [MEDIDO hoy]
attestor classify --role provider --annex-iii-area employment --bundle omnibus-2026 --checksum-only
# [ESPERADO] 3bc20cb8a68d47c16d36c91a400acd2e0b03eb2020f2983a14bdfc7a56fe24f0   [MEDIDO hoy]

pytest    # [ESPERADO] unos 240
```
Los dos checksums de arriba están **medidos hoy** por la vía de Python. Lo que no está medido es que exista el comando `attestor`, porque lo crea esta fase.

**Te devuelvo el control [TÚ]:** `git push -u origin feat/example-ledger-and-cli && gh pr create --fill && gh pr merge --merge`

**Horas: 3,5.**
**Nota al cerrar: 8,2.** La dimensión de los 20 minutos sube de 6,0 a 9,0.

---

### Fase 3: Puertas que muerden

**Objetivo:** convertir en contrato verificado lo que hoy es convención y buena suerte. Tres de las cuatro puertas entran en verde el primer día, porque miden algo que el repo ya cumple.

**Pasos [CC]:**

1. Rama: `git checkout -b ci/gates`

2. **Checksums anclados.** Este es el hueco que ni el plan anterior recogía: hoy **ningún test fija un valor de checksum**. Los goldens fijan riesgo y fechas, y los tests de determinismo comparan una ejecución consigo misma, o sea que un cambio en `canonical.py` pasaría la suite entera sin que nadie se entere, mientras el README vende "checksum reproducible que un auditor puede replicar".
   Crear `tests/golden/checksums.yaml` con los ocho valores de la sección 3 (los dos `sha256` de bundle históricos, el del bundle vigente cuando exista, y los checksums de clasificación por par perfil/bundle), y `tests/test_checksum_anchors.py` que los compruebe uno a uno.
   Trade-off: cualquier cambio legítimo en la canonicalización obligará a actualizar ese fichero a mano. Eso es exactamente lo que se quiere, porque es la decisión que hoy se toma sin enterarse.

3. **Contrato de capas.** Crear `tests/test_architecture.py` que recorra con `ast` los `import` de `src/attestor/{classifier,annexiv,ledger,provenance,governance}` y asevere: (a) ninguno importa `attestor.api`; (b) ninguno importa `openai`, `anthropic`, `langchain`, `litellm`, `httpx`, `requests` ni `socket`. [MEDIDO] las dos se cumplen hoy, o sea que la puerta entra verde. Convierte el titular del repo en contrato.

4. **Cobertura con umbral.** `pytest-cov` en dev, y en `[tool.pytest.ini_options]`:
   ```toml
   addopts = "-q --cov=src/attestor --cov-report=term-missing --cov-fail-under=95"
   ```
   El umbral va en 95 y no en 97 a propósito: dos puntos de margen para que un refactor legítimo no bloquee. [MEDIDO] la cobertura real es 97 %, 1085 statements, 35 missed.

5. **Código muerto.** `vulture` en dev y un paso de CI con `vulture src tests --min-confidence 80`. [MEDIDO] hoy da cero hallazgos: puerta gratis.

6. **Tipos.** `mypy` en dev con `types-reportlab`, y en `pyproject.toml`:
   ```toml
   [tool.mypy]
   python_version = "3.12"
   strict = true
   files = ["src/attestor"]

   [[tool.mypy.overrides]]
   module = ["c2pa.*"]
   ignore_missing_imports = true
   ```
   Arreglar los 31 errores según el desglose de la sección 3. **Presupuestado en 1,5 h, medido, no estimado.** Si a la hora y media quedan menos de cinco errores raros, se silencian con `# type: ignore[código]` **con comentario explicando por qué**, y se sigue. Lo que no vale es bajar a `strict = false` para esconderlos.

7. `.github/workflows/ci.yml`, después de la línea 32:
   ```yaml
      - name: Mypy
        run: mypy src/attestor

      - name: Dead code
        run: vulture src tests --min-confidence 80
   ```
   La cobertura no necesita paso propio: va dentro de `pytest` por el `addopts`.

8. `Makefile` con `install`, `check`, `demo`, `ledger`, `web`. `make check` ejecuta **exactamente** las mismas puertas que el CI, en el mismo orden.

9. `.pre-commit-config.yaml` con ruff check y ruff format pinados a `0.16.8`, la misma versión del CI. Es lo que impide que vuelva a pasar lo de la puerta de formato.

**Criterio de terminado [CC]:**
```bash
make check
# [ESPERADO] ruff OK, mypy Success, vulture sin salida, pytest verde con TOTAL >= 95%

# las puertas muerden de verdad, que es lo único que las valida:
echo "import httpx" >> src/attestor/classifier/engine.py
pytest tests/test_architecture.py          # [ESPERADO] FAILED
git checkout src/attestor/classifier/engine.py

sed -i 's/2026-08-02/2026-08-03/' src/attestor/classifier/rules/v2026-08.yaml
pytest tests/test_checksum_anchors.py      # [ESPERADO] FAILED
git checkout src/attestor/classifier/rules/v2026-08.yaml
```
Si alguna de esas dos no falla, la puerta no vale nada y hay que arreglarla antes de cerrar la fase.

**Te devuelvo el control [TÚ]:** `git push -u origin ci/gates && gh pr create --fill && gh pr merge --merge`

**Horas: 3,0.**
**Nota al cerrar: 8,7.** Ingeniería de 7,5 a 9,5, examen hostil a 9,0.

---

### Fase 4: El README y la procedencia

**Objetivo:** que el repo se entienda y se pruebe en 60 segundos, y que la velocidad de construcción esté declarada por ti y no descubierta por el revisor.

**Pasos [CC]:**

1. Rama: `git checkout -b docs/readme-final`

2. Mover a `docs/` las secciones profundas **tal cual, sin reescribirlas**: `README.md:138-204` a `docs/classifier.md`, `206-247` a `docs/annex-iv.md`, `249-331` a `docs/provenance.md`, `334-390` a `docs/ledger.md`, `393-439` a `docs/governance.md`, `442-478` a `docs/api.md`. No se borra nada: se recoloca.

3. Reescribir el README de 531 líneas a unas 230, con este orden: cabecera y badges (12), **Verify it in 60 seconds** (24), what it does (14), **Every claim and the command that proves it** (22), **Regulatory timeline: what changed and when** (16, nuevo, sale de `docs/regulatory-changelog.md`), arquitectura con el diagrama Mermaid actual sin tocar (32), run it locally (26), engineering (16), what this is not (30), provenance (10), deeper docs (12), roadmap (14), stack (14), license (4).

4. El bloque de 60 segundos, que tiene que aparecer **antes de la línea 40**:
   ````markdown
   ## Verify it in 60 seconds

   No keys, no network, no guessing.

   ```bash
   git clone https://github.com/marcosmatalab/attestor && cd attestor
   pip install -e .

   # 1. A third party verifies the committed ledger offline
   attestor ledger verify examples/ledger        # VERIFIED, exit 0

   # 2. Tamper with one byte and the verdict flips
   sed -i 's/sys-1/sys-9/' examples/ledger/records.json
   attestor ledger verify examples/ledger        # TAMPERED, exit 1
   git checkout examples/ledger/records.json

   # 3. Reproduce the checksum in the screenshot above
   attestor classify --role provider --annex-iii-area employment --checksum-only
   ```
   ````

5. La tabla de afirmaciones, que es la respuesta directa al examen hostil. Diez filas, cada una con su comando, y dos de ellas nuevas respecto al plan anterior:
   | Claim | Command | Expected |
   |---|---|---|
   | Adopting the Omnibus changed no golden vector | `pytest tests/test_regulatory_evolution.py` | Passes: the two historical bundles still hash to their June values |
   | The checksum is anchored, not just self consistent | `pytest tests/test_checksum_anchors.py` | Passes against committed literal digests |
   | y las ocho del plan anterior: determinismo, no LLM, capas, ledger offline, manipulación, firmante no confiable, cobertura, sin red | | |

6. El párrafo de procedencia, en su propia sección, antes de la licencia:
   > **Provenance.** This repository was built over four days in June 2026: 82 commits, 16 pull requests, one per phase. I used AI assistance to write code and documentation. The design decisions are mine, and they are the ones I would defend in an interview: storing effective dates **per obligation** rather than as one global date, which is why the Digital Omnibus becoming law in July 2026 was absorbed by adding a bundle instead of rewriting the engine; keeping **integrity and trust as two separate axes** in both C2PA and RFC3161, so an unrecognised signer never looks like a tampered file; and excluding default-valued fields from the canonical form, so adding questions to the questionnaire does not change the checksum of older inputs. The engine calls no LLM, and a test enforces it.

7. Badges. Quitar el de tests, que es un shields pintado a mano ([MEDIDO] la cifra 228 es exacta, pero nada obliga a que siga siéndolo). Quedan: CI real, release dinámico (`https://img.shields.io/github/v/release/marcosmatalab/attestor`) y licencia. El número de tests se dice en la sección Engineering, con el comando al lado.

8. La captura regenerada en la fase 0 va justo debajo del titular, envuelta en enlace a la demo desplegada, y con esta línea debajo: `The checksum in this screenshot is the one the command below reproduces.` Eso la convierte de decoración en evidencia. Guardar la original como `docs/dashboard-full.png` y poner en el README una versión de unos 1200 px de ancho: [MEDIDO] la actual es de 2360 x 2702 px y empuja el contenido ejecutable fuera de la primera pantalla.

**Criterio de terminado [CC]:**
```bash
wc -l README.md                  # [ESPERADO] por debajo de 250. Hoy 531 [MEDIDO]
grep -n '```bash' README.md | head -1   # [ESPERADO] línea por debajo de 40
grep -c "img.shields.io/badge/tests" README.md   # [ESPERADO] 0
# y cada comando de la tabla de afirmaciones se ejecuta y devuelve lo que dice
```

**Te devuelvo el control [TÚ]:** `git push -u origin docs/readme-final && gh pr create --fill && gh pr merge --merge`

**Horas: 2,25.**
**Nota al cerrar: 9,0.** Los 60 segundos suben a 9,0 y procedencia de 6,0 a 9,0.

---

### Fase 5: Señal externa y señal de vida

**Objetivo:** que haya prueba sin clonar, que el repo tenga versiones, y que estar vivo sea un hecho verificable en vez de una impresión.

**Pasos [CC]:**

1. Rama: `git checkout -b feat/pages-and-release`

2. Generar `web/public/demo-snapshot.json` con el motor:
   ```bash
   python -c "
   from fastapi.testclient import TestClient
   from attestor.api.main import app
   import json, pathlib
   r = TestClient(app).post('/api/demo/run')
   pathlib.Path('web/public/demo-snapshot.json').write_text(json.dumps(r.json(), indent=2))
   "
   ```

3. **La puerta del snapshot, que el plan anterior no tenía.** Crear `tests/test_demo_snapshot.py`: llama a `POST /api/demo/run` y compara los campos deterministas del resultado (riesgo, checksum de clasificación, `bundle_sha256`, fechas, `validation_state`, `trusted`) con los del JSON commiteado. Los no deterministas por diseño (raíz Merkle de claves efímeras, marcas de tiempo) se excluyen **con un comentario que diga por qué**. Sin esta puerta, en seis meses la demo desplegada enseña un checksum que el motor ya no produce, que es exactamente el fallo que la fase 2 arregla para el ledger.

4. `web/lib/api.ts`: `demo()` lee `/demo-snapshot.json` cuando `NEXT_PUBLIC_DEMO_SNAPSHOT === "1"`, y mantiene el POST actual en cualquier otro caso. En local contra el backend sigue funcionando igual que hoy.

5. `web/next.config.ts`: `output: "export"`, `images: { unoptimized: true }`, `basePath: process.env.NEXT_PUBLIC_BASE_PATH ?? ""`. El `basePath` hace falta porque Pages sirve en `/attestor`. [MEDIDO] las 3 rutas ya salen estáticas en el build actual.

6. Aviso en la página desplegada, visible, no en letra pequeña:
   > This deployed demo renders a snapshot generated by the engine at commit `<sha>`. Every value came from a real run: nothing here is hand written. A test in CI fails if the engine stops producing it. To run it live, clone the repo and start the backend.

7. `.github/workflows/pages.yml`: `npm ci`, build con `NEXT_PUBLIC_DEMO_SNAPSHOT=1` y `NEXT_PUBLIC_BASE_PATH=/attestor`, y publicación de `web/out`.

8. **`.github/workflows/heartbeat.yml`, la señal de vida honesta.** Un workflow con `schedule: cron` semanal más `workflow_dispatch`, que instala el paquete y ejecuta el guion de aceptación entero: suite completa, verificación de `examples/ledger`, comprobación de los checksums anclados y del hash de los bundles históricos. No commitea nada, no toca el árbol. Lo que produce es una ejecución verde fechada en la pestaña Actions, todas las semanas, y un aviso cuando algo envejezca mal. Un commit de relleno finge actividad; esto la demuestra.

9. `CHANGELOG.md` con dos entradas: `v0.1.0` y una línea para la adopción del Reglamento 2026/1744, con su fecha.

10. Subir la versión de `src/attestor/__init__.py` de `0.0.1` a `0.1.0`, para que el tag y el wheel no se contradigan.

**Te devuelvo el control [TÚ]:**
```bash
git push -u origin feat/pages-and-release
gh pr create --fill && gh pr merge --merge
git checkout main && git pull

git tag -a v0.1.0 -m "First tagged release: deterministic classifier under Reg. (EU) 2026/1744, Annex IV, C2PA, offline-verifiable ledger"
git push --tags
python -m build
gh release create v0.1.0 dist/*.whl examples/ledger/records.json examples/ledger/signed_root.json
```
Ojo: el plan anterior ponía `gh release create v0.10` en este mismo paso, con el tag `v0.1.0`. Es una errata que rompe el comando.

Y tres cosas en el navegador, diez minutos:
- Settings, Pages, origen: GitHub Actions.
- `About` del repo: `Deterministic EU AI Act classification engine (Reg. (EU) 2026/1744) with an offline-verifiable cryptographic ledger. Python, FastAPI, Next.js.` Website: la URL de Pages.
- Topics: `eu-ai-act`, `ai-governance`, `compliance`, `c2pa`, `content-credentials`, `merkle-tree`, `ed25519`, `fastapi`.

**Criterio de terminado [TÚ]:**
```bash
curl -s https://marcosmatalab.github.io/attestor/demo | grep -c "VERIFIED"   # [ESPERADO] >= 1
mkdir -p /tmp/r && cd /tmp/r
curl -sLO <url del records.json de la release>
curl -sLO <url del signed_root.json de la release>
attestor ledger verify /tmp/r      # [ESPERADO] VERIFIED, exit 0
```
Ese último comando es el que cierra la dimensión de los 60 segundos: **verificar el ledger sin clonar el repo**.

**Horas: 2,75.**
**Nota al cerrar: 9,5.** Señal externa de 2,0 a 9,0.

---

## 6. Resumen y cortes

| Fase | Horas | Nota al cerrar |
|---|---|---|
| 0. Vigencia regulatoria | 3,5 | 7,0 |
| 1. La verdad | 1,5 | 7,6 |
| 2. Reproducibilidad | 3,5 | 8,2 |
| 3. Puertas que muerden | 3,0 | 8,7 |
| 4. README y procedencia | 2,25 | 9,0 |
| 5. Señal externa y vida | 2,75 | 9,5 |
| **Total** | **16,5** | **9,5** |

**Si solo haces una cosa:** la fase 0. Es la única que arregla una falsedad y a la vez te da el argumento de venta del repo.
**Si haces tres:** 0, 1 y 2, **8,5 h**, te dejan en 8,2. Con eso el repo no dice nada falso, cualquiera verifica el ledger con un comando y tienes una historia de dominio que ningún otro repo tuyo tiene. **Este es el corte que yo haría si el tiempo aprieta.**
**Coste por décima:** de 5,5 a 8,2 son 8,5 h, o sea 3,1 h por punto. De 8,2 a 9,5 son 8,0 h, o sea 6,2 h por punto. La segunda mitad cuesta el doble por punto que la primera. Si el objetivo es tener trabajo y no tener un 9,5, párate en 8,2 y dedica las otras 8 horas a mandar candidaturas.

---

## 7. Guion de aceptación

Lo que ejecuta un tercero sobre un clon limpio para comprobar que el repo está en 9,5.

```bash
git clone https://github.com/marcosmatalab/attestor && cd attestor
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 1. Vigencia del dominio
python -c "from attestor.classifier import load_bundle as L; b=L(); print(b.version, b.meta['status'], b.meta['in_force_since'])"
# [ESPERADO] reg-2026-1744 in-force 2026-07-27
grep -rn "pending formal adoption\|not yet in force" README.md src/ web/lib
# [ESPERADO] cero aciertos fuera del bundle histórico

# 2. La adopción no tocó nada histórico
pytest tests/test_regulatory_evolution.py     # [ESPERADO] passed
python -c "from attestor.classifier import load_bundle as L; print(L('v2026-08').sha256)"
# [ESPERADO] 7e77bc0715a2b5836f83e6c50e69ab312ca8b7167c1c747674d8143a3312d49d   [MEDIDO hoy]

# 3. Puertas
make check
# [ESPERADO] ruff OK, mypy Success, vulture sin salida, pytest verde, cobertura >= 95%
pytest tests/test_checksum_anchors.py tests/test_architecture.py   # [ESPERADO] passed

# 4. Sin red
HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 pytest -q
# [MEDIDO en el HEAD de hoy] 228 passed, exit 0. La suite no toca la red

# 5. Un tercero verifica
attestor ledger verify examples/ledger                    # [ESPERADO] VERIFIED, exit 0
sed -i 's/sys-1/sys-9/' examples/ledger/records.json
attestor ledger verify examples/ledger                    # [ESPERADO] TAMPERED, exit 1
git checkout examples/ledger/records.json

# 6. Checksums, los dos escenarios
attestor classify --role provider --annex-iii-area employment --bundle v2026-08 --checksum-only
# [MEDIDO] 15815cd8f577dea7cc09696acc9a3e96870664573ea428e7c81bb8b06a84bd17
attestor classify --role provider --annex-iii-area employment --bundle omnibus-2026 --checksum-only
# [MEDIDO] 3bc20cb8a68d47c16d36c91a400acd2e0b03eb2020f2983a14bdfc7a56fe24f0

# 7. Frontend
cd web && npm ci && npm run lint && npm run build && npm run typecheck && npm test && cd ..
# [MEDIDO en el HEAD de hoy] todo exit 0, 20 tests de vitest, 3 rutas estáticas

# 8. Presentación y señal
wc -l README.md            # [ESPERADO] < 250    (hoy 531 [MEDIDO])
git ls-remote --heads origin   # [ESPERADO] una línea: refs/heads/main   (hoy 7 [MEDIDO])
git tag -l                 # [ESPERADO] v0.1.0   (hoy vacío [MEDIDO])
```

---

## 8. Lo que este plan no compra

- **La adopción por terceros.** Cero forks, cero issues ajenos. No se compra con horas y este plan no lo intenta. Lo más cerca: escribir en algún sitio sobre cómo modelaste fechas por obligación y por eso la entrada en vigor del Omnibus te costó un bundle y cero goldens. Eso sí es material publicable y ahora tienes el caso real, que en junio no tenías.

- **La cadencia, aunque este plan la mejora.** El workflow semanal demuestra que el repo funciona, no que lo estés desarrollando. Un revisor distingue las dos cosas. Sigue haciendo falta un commit pequeño de vez en cuando, y eso no cabe en un criterio de terminado.

- **El calendario del historial.** 82 commits en cuatro días de junio se queda en `git log` para siempre. La fase 4 lo declara en vez de disimularlo, porque reescribir el historial huele mucho peor y además rompe los 16 PRs, que hoy son buena señal.

- **Haber integrado un KMS.** Sigue siendo no. Lo que el plan te compra es poder decir "tengo la costura y no he querido fingir la integración", que se defiende. No es lo mismo que haberlo hecho.

- **Que el dominio se quede quieto.** Esto ya te ha pasado una vez: el repo era correcto el 23 de junio y dejó de serlo el 27 de julio sin que nadie tocara nada. Va a volver a pasar. El workflow semanal no lo detecta, porque un cambio normativo no rompe ningún test. Lo único que funciona es mirarlo antes de cada ronda de candidaturas: veinte minutos, y ahora ya sabes exactamente dónde mirar, en `meta.status_note`.

- **Que Attestor deje de ser un repo de compliance.** Con la fase 0 puedes contarlo como ingeniería, que es lo que quieres vender, pero el dominio sigue siendo el AI Act. Es un repo para enseñar, no el que te define.

---

## 9. Registro de decisiones

### ADR 1: Bundles inmutables, el cambio regulatorio se añade

**Decisión.** Crear `reg-2026-1744.yaml` en vez de editar `omnibus-2026.yaml`.

**Contexto.** [MEDIDO] tocar `meta.status_note` del bundle Omnibus cambia su `sha256` de `a52cb5e1...` a `e2a81819...`, y con él todos los checksums derivados. El repo ancla hashes de bundle en el ledger: reescribir un artefacto ya anclado es justo lo que un sistema de evidencia no debe hacer.

**Alternativa descartada.** Editar el bundle. Más rápido, media hora menos, y destruye el argumento de que el bundle provisional de junio sigue intacto y comparable con el vigente.

**Consecuencia.** Tres bundles, dos históricos, y una sección de README que explica cuál es cuál. El `git diff` vacío sobre los goldens es la prueba de la fase 0, y la fase 3 la vuelve permanente.

### ADR 2: El bundle por defecto es el derecho vigente

**Decisión.** `DEFAULT_VERSION` pasa a `reg-2026-1744` y la captura se regenera.

**Contexto.** Un motor de cumplimiento que por defecto aplica un calendario derogado es incorrecto, y es lo primero que pregunta quien conozca el expediente.

**Alternativa descartada.** Mantener el defecto para conservar `15815cd8...` y no rehacer la captura. Ahorra media hora a cambio de dejar mal la decisión más visible.

**Consecuencia.** 12 llamadas a `load_bundle()` sin argumento pasan a ser explícitas, que además es mejor estilo, y la captura se rehace una vez.

### ADR 3: Declarar la costura de KMS en vez de implementarlo

**Decisión.** Borrar la afirmación de capacidad y describir `Signer.from_callback` como el punto de enganche que es.

**Contexto.** [MEDIDO] 20 aciertos de `kms|hsm|boto3|aws` y ninguno es código. Se desmonta con un `grep` en diez segundos.

**Alternativa descartada.** Implementar `KmsSigner` con `boto3` y testear contra `moto`. Son días, añade una dependencia pesada y rompe la mejor propiedad del repo, que la suite entera corre sin red. Y un revisor distingue un test contra `moto` de una integración real.

**Consecuencia.** El roadmap pierde un reclamo y gana que ninguna fila se pueda desmentir.

### ADR 4: Pinar exactamente, incluidas las actions

**Decisión.** Versiones exactas en `pyproject.toml` y SHA completos en las actions del workflow.

**Contexto.** [MEDIDO] la puerta `ruff format --check .` da exit 0 con ruff 0.8.6 y exit 1 con 0.16.8, y el fichero que rompe es el README, no el código: ruff 0.16 empezó a formatear bloques de Python dentro de Markdown. Nadie tocó el repo, envejeció solo.

**Alternativa descartada.** Rangos abiertos más Dependabot. Para un repo de portfolio, catorce PRs de bump sin mergear transmiten abandono mejor que el silencio.

**Consecuencia.** El CI de dentro de seis meses da lo mismo que el de hoy. Actualizar pasa a ser una decisión con su commit.

### ADR 5: Snapshot desplegado solo con test que lo ate al motor

**Decisión.** `web/public/demo-snapshot.json` se commitea únicamente junto a `tests/test_demo_snapshot.py`.

**Contexto.** El plan anterior commiteaba el snapshot sin puerta, que es el mismo fallo que ese plan corrige para el ledger. Un snapshot sin test se desincroniza en silencio y acaba enseñando cifras que el motor ya no produce.

**Alternativa descartada.** Desplegar con backend en Vercel para que la demo sea totalmente viva. Cuesta entre 3 y 4 h más mantenimiento, necesita un endpoint público que genera claves efímeras por petición, y añade factura y superficie de ataque a cambio de poco.

**Consecuencia.** La demo desplegada es honesta y verificable, y el día que el motor cambie, el CI se entera antes que el visitante.

---

## Fuentes de la parte regulatoria

- Consejo de la UE, luz verde definitiva, 29 jun 2026: https://www.consilium.europa.eu/en/press/press-releases/2026/06/29/artificial-intelligence-council-gives-final-green-light-to-simplify-and-streamline-rules/
- Entrada en vigor, 27 jul 2026 (Lewis Silkin): https://www.lewissilkin.com/insights/2026/07/27/the-digital-omnibus-on-ai-enters-into-force-today-102nedo
- Reglamento (UE) 2026/1744 publicado en el DOUE: https://www.nicfab.eu/en/posts/digital-omnibus-ai-official-journal/
- White & Case, qué modifica exactamente del AI Act: https://www.whitecase.com/insight-alert/eu-ai-omnibus-enters-force-amending-ai-act

Antes de dar por buena la fase 0, comprueba tú el texto consolidado en EUR-Lex. Las cuatro fuentes de arriba coinciden en fechas, pero el que manda es el DOUE.

