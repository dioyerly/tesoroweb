from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class Empresa(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  nombre = db.Column(db.String(100), nullable=False)
  cuit = db.Column(db.String(20), unique=True, nullable=False)
  estado_suscripcion = db.Column(db.String(20), default='activa')
  fecha_alta = db.Column(db.DateTime, default=datetime.utcnow)


class Usuario(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=True)
  nombre = db.Column(db.String(100), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password_hash = db.Column(db.String(255), nullable=False)
  cargo = db.Column(db.String(100), nullable=True)
  rol = db.Column(db.String(50), default='Operador')
  sociedades_permitidas = db.Column(db.String(255), default='*')
  activo = db.Column(db.Boolean, default=True)
  debe_cambiar_password = db.Column(db.Boolean, default=True)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)


class Sociedad(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  empresa_id = db.Column(
      db.Integer, db.ForeignKey('empresa.id'), nullable=False
  )
  nombre = db.Column(db.String(100), nullable=False)
  cuit = db.Column(db.String(20), nullable=False)
  direccion = db.Column(db.String(200), nullable=True)


class BancoSociedad(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  sociedad_id = db.Column(
      db.Integer, db.ForeignKey('sociedad.id'), nullable=False
  )
  nombre_banco = db.Column(db.String(100), nullable=False)
  cbu = db.Column(db.String(50), nullable=True)


class Proveedor(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  empresa_id = db.Column(
      db.Integer, db.ForeignKey('empresa.id'), nullable=False
  )
  cuit = db.Column(db.String(20), nullable=False)
  nombre = db.Column(db.String(100), nullable=False)
  cbu_alias = db.Column(db.String(100), nullable=True)


class FacturaPago(db.Model):
  __tablename__ = 'factura_pago'
  __table_args__ = {'extend_existing': True}

  id = db.Column(db.Integer, primary_key=True)
  empresa_id = db.Column(
      db.Integer, db.ForeignKey('empresa.id'), nullable=False
  )
  sociedad_id = db.Column(
      db.Integer, db.ForeignKey('sociedad.id'), nullable=True
  )
  proveedor_id = db.Column(
      db.Integer, db.ForeignKey('proveedor.id'), nullable=True
  )
  banco_origen_id = db.Column(
      db.Integer, db.ForeignKey('banco_sociedad.id'), nullable=True
  )
  nro_factura = db.Column(db.String(50))
  nro_oc_op = db.Column(db.String(50), nullable=True)
  monto = db.Column(db.Float, nullable=False)
  fecha_vencimiento = db.Column(db.Date, nullable=True)
  fecha_pago_programada = db.Column(db.Date, nullable=True)
  tipo_gasto = db.Column(db.String(20), default='proveedor')
  forma_pago = db.Column(db.String(50), default='Transferencia')
  numero_cheque = db.Column(db.String(50), nullable=True)
  descripcion = db.Column(db.String(255), nullable=True)
  estado = db.Column(db.String(20), default='pendiente')


class Recordatorio(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  empresa_id = db.Column(
      db.Integer, db.ForeignKey('empresa.id'), nullable=False
  )
  usuario_id = db.Column(
      db.Integer, db.ForeignKey('usuario.id'), nullable=False
  )
  fecha = db.Column(db.Date, nullable=False)
  nota = db.Column(db.String(255), nullable=False)
  hecho = db.Column(db.Boolean, default=False, nullable=False)
  recurrencia = db.Column(db.String(30), default='unica', nullable=False)


class Conciliacion(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  empresa_id = db.Column(
      db.Integer, db.ForeignKey('empresa.id'), nullable=False
  )
  fecha_procesamiento = db.Column(db.DateTime, default=datetime.utcnow)
  estado = db.Column(db.String(20), default='pendiente')
  archivo_nombre = db.Column(db.String(255), nullable=False)


class MovimientoBancario(db.Model):
  __table_args__ = (
      db.UniqueConstraint(
          'empresa_id', 'hash_dedup', name='uq_movimiento_empresa_hash'
      ),
  )

  id = db.Column(db.Integer, primary_key=True)
  empresa_id = db.Column(
      db.Integer, db.ForeignKey('empresa.id'), nullable=False
  )
  fecha = db.Column(db.Date, nullable=False)
  monto = db.Column(db.Float, nullable=False)
  tipo = db.Column(db.String(10), nullable=False)  # 'debito' o 'credito'
  descripcion = db.Column(db.Text, nullable=True)
  hash_dedup = db.Column(db.String(64), nullable=False)
  estado = db.Column(db.String(20), default='sin_conciliar')
  factura_pago_id = db.Column(
      db.Integer, db.ForeignKey('factura_pago.id'), nullable=True
  )
  # 'pago' (transferencias/débitos a proveedores), 'impuesto_gasto' (IVA,
  # Ingresos Brutos, Ley 25413, comisiones bancarias) o 'ingreso' (créditos).
  categoria = db.Column(db.String(20), default='pago')
  conciliado_manual = db.Column(db.Boolean, default=False, nullable=False)
  archivo_origen = db.Column(db.String(255), nullable=True)
  fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)


class MovimientoSplit(db.Model):
  __tablename__ = 'movimiento_split'
  id = db.Column(db.Integer, primary_key=True)
  movimiento_bancario_id = db.Column(
      db.Integer, db.ForeignKey('movimiento_bancario.id'), nullable=False
  )
  factura_pago_id = db.Column(
      db.Integer, db.ForeignKey('factura_pago.id'), nullable=False
  )
  monto_asignado = db.Column(db.Float, nullable=False)
  fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow)


class ConciliacionAuditoria(db.Model):
  __tablename__ = 'conciliacion_auditoria'
  id = db.Column(db.Integer, primary_key=True)
  empresa_id = db.Column(
      db.Integer, db.ForeignKey('empresa.id'), nullable=False
  )
  movimiento_bancario_id = db.Column(
      db.Integer, db.ForeignKey('movimiento_bancario.id'), nullable=False
  )
  factura_pago_id = db.Column(
      db.Integer, db.ForeignKey('factura_pago.id'), nullable=True
  )
  tipo_conciliacion = db.Column(db.String(50), nullable=False)
  regla_aplicada = db.Column(db.String(255), nullable=False)
  confianza = db.Column(db.Float, default=1.0)
  usuario = db.Column(db.String(100), default='SYSTEM_AUTO')
  timestamp = db.Column(db.DateTime, default=datetime.utcnow)
  monto_conciliado = db.Column(db.Float, nullable=False)
  notas = db.Column(db.Text, nullable=True)