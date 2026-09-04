# Datos de Demostración - Tesorería App

## Resumen de la Carga Demo

Se ha cargado un conjunto completo de datos falsos realistas para usar en videos, presentaciones y demostraciones. Los datos no comprometen información real y son totalmente ficticios.

**Nombre de la Empresa:** Empresa Demo Argentina S.A. (nombre genérico para no confundir con empresas reales)

---

## Credenciales de Acceso

### Cuenta Administrador Principal

**Email:** `jmartinez@andamios.com`
**Contraseña:** `Demo1234`
**Rol:** Administrador
**Nombre:** Juan Carlos Martínez
**Cargo:** Administrador General

---

## Empleados Disponibles

Todos los empleados usan la misma contraseña: **Demo1234**

| Nombre | Email | Rol | Cargo |
|--------|-------|-----|-------|
| Juan Carlos Martínez | jmartinez@andamios.com | Administrador | Administrador General |
| María Fernanda López | mlopez@andamios.com | Operador | Tesorera |
| Roberto Silva | rsilva@andamios.com | Contador | Contador |
| Ana González | agonzalez@andamios.com | Operador | Asistente de Tesorería |
| Diego Rodríguez | drodriguez@andamios.com | Supervisor | Supervisor de Caja |

---

## Estructura de la Empresa

### Empresa: Empresa Demo Argentina S.A.
- **CUIT:** 30987654321 (falso)
- **Estado de Suscripción:** Activa

---

## Sociedades (3 Total)

### 1. Constructora Centro S.R.L.
- **CUIT:** 30456789012 (falso)
- **Dirección:** Av. 9 de Julio 1234, CABA
- **Bancos Asociados:** 4
  - Banco Galicia (CBU: 0070123456789012345)
  - Banco BBVA Argentina (CBU: 0150987654321098765)
  - Banco Santander Río (CBU: 0072456789012345678)
  - Banco ICBC (CBU: 0060789012345678901)

### 2. Servicios Logísticos S.A.
- **CUIT:** 33876543210 (falso)
- **Dirección:** Ruta 5 km 35, La Matanza, Buenos Aires
- **Bancos Asociados:** 4 (mismos bancos que sociedad 1)

### 3. Consultora Técnica S.R.L.
- **CUIT:** 30765432109 (falso)
- **Dirección:** Balcarce 456, San Isidro, Buenos Aires
- **Bancos Asociados:** 4 (mismos bancos que sociedad 1)

---

## Proveedores (27 Total)

Se han cargado 27 proveedores con nombres realistas y CUITs falsos:

- Distribuidora de Materiales Hnos. García S.A.
- Aceros Inoxidables del Sur S.R.L.
- Química Industrial Ltda.
- Transportes Rápidos S.A.
- Maderas y Compensados S.R.L.
- Pinturas Premium Argentina S.A.
- Herramientas Profesionales Ltda.
- Seguridad Industrial del Centro S.A.
- Equipos Electromecánicos Ltda.
- Combustibles y Lubricantes S.R.L.
- Vidrio Templado Buenos Aires S.A.
- Sanitarios y Griferías S.R.L.
- Sistemas de Aire Acondicionado S.A.
- Cables y Conductores Eléctricos Ltda.
- Tuberías Plásticas Premium S.R.L.
- Cerraduras y Cerrajería Ltda.
- Puertas y Ventanas Integral S.A.
- Pisos y Revestimientos Mármol S.R.L.
- Estructuras Metálicas Reforzadas Ltda.
- Aislantes Térmicos Nacionales S.A.
- Cerámicas Decorativas Ltda.
- Tornillería Industrial Premium S.R.L.
- Y 5 proveedores adicionales generados

Cada proveedor tiene:
- CUIT falso de 11 dígitos
- Nombre comercial realista
- Alias/CBU falso para transferencias

---

## Facturas y Pagos (25 Total)

Se han cargado 25 facturas con datos realistas:

### Distribución de Estados
- **Pagadas:** 9 facturas
- **Pendientes:** 16 facturas

### Características de cada factura
- Número de factura formateado (PPPPP-CCCCCCCC)
- Monto entre ARS $500 y ARS $50.000
- Fechas de vencimiento y pagos distribuidas en +/- 30-60 días
- Asociadas a distintas sociedades y proveedores
- Formas de pago: Transferencia, Cheque, Efectivo
- Algunas con número de cheque registrado
- Números de OC/OP para referencia

---

## Movimientos Bancarios (11 Total)

Para demostrar la función de Conciliación Bancaria:

- **Conciliados:** 6 movimientos (asociados a facturas pagadas)
- **Sin Conciliar:** 5 movimientos (para ejemplificar reconciliación pendiente)

Cada movimiento incluye:
- Fecha del movimiento
- Monto
- Tipo: Débito o Crédito
- Descripción detallada
- Hash de deduplicación (para evitar duplicados)
- Categoría: Pago, Impuesto/Gasto, o Ingreso

---

## Recordatorios en Agenda (10 Total)

Recordatorios pre-cargados en el calendario para demostración:

1. Revisar conciliación bancaria (en 3 días)
2. Pagar facturas del período anterior (en 1 día)
3. Auditoría interna de tesorería (en 7 días)
4. Reunión con contador (en 5 días)
5. Cierre de mes contable (en 10 días)
6. Verificar disponibilidad de fondos (hoy)
7. Preparar reporte de flujo de caja (en 2 días)
8. Validar pagos en proceso (en 1 día)
9. Contactar proveedores morosos (en 4 días)
10. Arqueo de caja (en 6 días)

---

## Qué Puedes Hacer con Estos Datos

### Panel Principal
- Visualizar resumen de pagos pendientes y próximos a vencer
- Métricas de flujo de caja por día y por período
- Recordatorios de agenda visible

### Gestión de Pagos
- Ver lista completa de facturas con filtros por:
  - Sociedad
  - Fecha de pago
  - Forma de pago
  - Estado (pagado/pendiente)
- Editar fechas de pago
- Marcar como pagado/pendiente
- Exportar a Excel

### Configuración
- Ver/editar sociedades
- Ver/editar bancos asociados
- Ver/editar lista de proveedores
- Gestionar usuarios y empleados
- Importar/exportar proveedores desde Excel

### Conciliación Bancaria
- Visualizar movimientos bancarios
- Conciliar automáticamente con facturas
- Identificar movimientos sin conciliar

---

## Notas Importantes

1. **Todos los CUIT, CBU y alias son ficticios** - No corresponden a entidades reales
2. **Los datos son solo para demostración** - No guardes información sensible aquí
3. **Reemplaza estos datos** antes de usar en producción con datos reales
4. **La contraseña Demo1234 es insegura** - Cámbiala en producción
5. **Datos de prueba generados:** 2 de septiembre de 2026

---

## Cómo Usar Para Videos/Presentaciones

1. **Iniciar sesión** con las credenciales del Administrador
2. **Panel Principal:** Muestra resumen de pagos pendientes y próximos
3. **Gestión de Pagos:** Visualiza las 25 facturas con diferentes estados
4. **Configuración:** Muestra 5 empleados, 3 sociedades y 27 proveedores
5. **Conciliación:** Demuestra 6 movimientos conciliados y 5 pendientes
6. **Agenda:** Muestra 10 recordatorios distribuidos en el calendario

---

## Si Necesitas Más Datos

Ejecuta nuevamente el script `seed_demo.py` para regenerar los datos:

```bash
python seed_demo.py
```

Este script es idempotente - si ciertos datos ya existen, no los duplicará.

---

**Creado:** 2026-09-02  
**Para:** Demostraciones y Videos  
**Estado:** Listo para usar  
