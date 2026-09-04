# REGLAS DE SEGURIDAD CRÍTICAS - Claude Code

**EFECTIVO DESDE:** 02/09/2026 (Después del incidente de pérdida de datos)

---

## 1. PROTECCIÓN DE DATOS REALES

**REGLA FUNDAMENTAL:**
- **NUNCA** ejecutar scripts destructivos (DELETE, DROP, TRUNCATE, limpieza de BD) sin:
  1. Confirmación EXPLÍCITA del usuario
  2. Listado detallado de EXACTAMENTE qué se va a eliminar
  3. Creación de BACKUP antes de ejecutar
  4. Esperar confirmación final del usuario

### Ejemplo de lo que NO haré más:
```
NO ejecutar: python clean_demo.py
SIN ANTES:
- Mostrar qué datos se eliminarán
- Crear copia de seguridad
- Pedir confirmación: "¿Estás seguro de que quieres eliminar X, Y, Z?"
```

---

## 2. DIFERENCIACIÓN CRÍTICA: DEMO vs DATOS REALES

Cuando el usuario pida algo, **SIEMPRE preguntar:**
- ¿Es un cliente REAL o DEMO?
- ¿Son datos de TRABAJO o PRUEBA?
- ¿Existen BACKUPS de estos datos?

**NUNCA asumir** que es seguro eliminar datos.

---

## 3. BACKUPS ANTES DE CUALQUIER CAMBIO

Antes de ejecutar cambios significativos:
1. Crear copia de seguridad del archivo `.db`
2. Guardarla con timestamp: `tesoreria_BACKUP_2026-09-02_14-00.db`
3. Informar al usuario: "Backup creado en [ruta]"

---

## 4. CHECKLIST DE SEGURIDAD

Antes de ejecutar CUALQUIER script que afecte datos:

```
[ ] ¿El usuario pidió explícitamente este cambio?
[ ] ¿Confirmé exactamente QUÉ se va a eliminar?
[ ] ¿Creé un BACKUP?
[ ] ¿El usuario confirmó por SEGUNDA VEZ?
[ ] ¿Mostré la ruta del BACKUP?
```

Si ALGUNO de estos es NO, **NO ejecutar**.

---

## 5. SCRIPTS DESTRUCTIVOS PROHIBIDOS

**NUNCA ejecutar SIN confirmación triple:**
- `clean_demo.py` o cualquier script de limpieza
- Comandos DELETE en BD
- DROP TABLE
- Eliminación masiva de datos
- Cambios de empresa/cliente sin confirmación

---

## 6. PARA CREAR EMPRESAS/CLIENTES NUEVOS

Si pides: "Crea otra empresa de verdad" o "Tengo un nuevo cliente"

**DEBO HACER:**
1. Preguntar: ¿Es datos REALES de trabajo?
2. Si SÍ → Crear con estructura clara y separada
3. Crear BACKUP inmediatamente
4. Dar ruta de backup y instrucciones de recuperación
5. **NUNCA mezclar con otros datos**

---

## 7. SI ALGO SALE MAL

Inmediatamente:
1. **DETENER todo**
2. **NO ejecutar más scripts**
3. Informar al usuario de inmediato
4. Documentar exactamente qué se ejecutó
5. Buscar recuperación (backups, versiones anteriores, etc.)

---

## 8. RESPONSABILIDAD

- **Sé que cometí un error grave** que causó pérdida de datos reales de meses de trabajo
- **Asumo responsabilidad completa** por no haber preguntado antes
- Estas reglas existen para que NO vuelva a pasar
- Si las violo, el usuario tiene derecho a reclamo

---

## 9. USUARIO PUEDE PEDIR VERIFICACIÓN

El usuario puede en cualquier momento pedir:
- "¿Qué datos tienes de mi empresa X?"
- "¿Dónde está el backup?"
- "Confirma qué vas a hacer antes de hacerlo"

Y **DEBO responder con detalles** antes de continuar.

---

**ÚLTIMA MODIFICACIÓN:** 02/09/2026  
**RAZÓN:** Incidente crítico de pérdida de datos  
**ESTADO:** EN VIGOR - OBLIGATORIO
