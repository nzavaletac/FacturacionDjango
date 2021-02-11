from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from Almacen.models import InventarioModel


class UsuarioManager(BaseUserManager):
    """Manejo del modelo del usuario"""

    def create_user(self, email, nombre, apellido, tipo, password=None):
        """Creacion de un nuevo usuario comun y corriente"""
        if not email:  # si no hay correo, mandare un error
            raise ValueError(
                "El usuario debe tener obligatoriamente un correo")
        # normalizo el email que aparte de ver si hay el @ y . todo lo llevar a lowerCase (minusculas y quitara los espacios que pudiesen haber)
        email = self.normalize_email(email)
        # creo mi objeto de usuario pero aun no lo guarod en la bd
        usuario = self.model(usuarioCorreo=email, usuarioNombre=nombre,
                             usuarioApellido=apellido, usuarioTipo=tipo)
        # con este paso se encripta la contraseña
        usuario.set_password(password)
        usuario.save(using=self._db)  # acá recien se guarda en la bd
        return usuario

    def create_superuser(self, usuarioCorreo, usuarioNombre, usuarioApellido, usuarioTipo, password):
        """Creacion de un nuevo super usuario que pueda acceder a todas las opciones del panel administrativo"""
        user = self.create_user(
            usuarioCorreo, usuarioNombre, usuarioApellido, usuarioTipo, password)
        # este campo se crea automaticamente por la herencia de la clase PermissionsMixin
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)


class UsuarioModel(AbstractBaseUser, PermissionsMixin):
    """Modelo de la base de datos de los usuarios del sistema"""
    TIPOS_USUARIO = [
        (1, 'ADMINISTRADOR'),
        (2, 'CAJERO'),
        (3, 'MOZO')
    ]
    usuarioId = models.AutoField(
        primary_key=True,
        unique=True,
        db_column='usu_id'
    )
    usuarioCorreo = models.EmailField(
        db_column="usu_mail",
        max_length=50,
        unique=True,
        verbose_name='Correo del usuario'
    )
    usuarioNombre = models.CharField(
        db_column="usu_nombre",
        max_length=40,
        verbose_name='Nombre del usuario'
    )
    usuarioApellido = models.CharField(
        db_column="usu_apellido",
        max_length=50,
        verbose_name="Apellido del usuario"
    )
    usuarioTipo = models.IntegerField(
        db_column="usu_tipo",
        help_text="Tipo del usuario",
        choices=TIPOS_USUARIO,
        verbose_name='Tipo del usuario'
    )
    password = models.TextField(
        db_column="usu_pass",
        verbose_name='Contraseña del usuario')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()
    USERNAME_FIELD = 'usuarioCorreo'
    REQUIRED_FIELDS = ['usuarioNombre', 'usuarioApellido', 'usuarioTipo']

    def __str__(self):
        return self.usuarioCorreo

    class Meta:
        db_table = "t_usuario"
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

# Comandos para la migracion
# py manage.py makemigrations Facturacion
# py manage.py showmigrations
# py manage.py migrate


class MesaModel(models.Model):
    mesaId = models.AutoField(
        primary_key=True,
        null=False,
        db_column='mesa_id'
    )
    mesaNumero = models.CharField(
        max_length=15,
        db_column='mesa_numero',
        null=False
    )
    mesaCapacidad = models.IntegerField(
        db_column='mesa_capacidad',
        null=False
    )
    mesaEstado = models.BooleanField(
        db_column='mesa_estado',
        default=True,
        null=False
    )

    def __str__(self):
        return 'El Numero de la mesa es: '+self.mesaNumero

    class Meta:
        db_table = 't_mesa'
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'


class CabeceraComandaModel(models.Model):
    cabeceraId = models.AutoField(
        primary_key=True,
        null=False,
        unique=True,
        db_column='cabecera_id'
    )
    cabeceraFecha = models.DateField(
        null=False,
        db_column='cabecera_fecha',
        verbose_name='Fecha del pedido'
    )
    cabeceraTotal = models.DecimalField(
        decimal_places=2,
        max_digits=5,
        db_column='cabecera_total',
        null=False,
        verbose_name='Total del pedido'
    )
    cabeceraCliente = models.CharField(
        db_column='cabecera_cliente',
        null=False,
        max_length=50,
        verbose_name='Nombre del Cliente'
    )
    cabeceraEstado = models.CharField(
        db_column='cabecera_estado',
        null=False,
        max_length=50,
        verbose_name='Estado del pedido',
        default='ABIERTO'
    )
    # Luego creamos las relaciones
    mesa = models.ForeignKey(
        to=MesaModel,
        db_column='mesa_id',
        verbose_name='Mesa',
        on_delete=models.PROTECT,
        related_name='mesaComandas'
    )

    usuario = models.ForeignKey(
        to=UsuarioModel,
        db_column='mesero_id',
        verbose_name='Usuario',
        on_delete=models.PROTECT,
        related_name='usuarioComandas'
    )

    def __str__(self):
        return self.cabeceraCliente

    class Meta:
        db_table = 't_comanda_cabecera'
        verbose_name = 'Comanda'
        verbose_name_plural = 'Comandas'


class ComprobanteModel(models.Model):
    comprobanteId = models.AutoField(
        primary_key=True,
        null=False,
        unique=True,
        db_column='comprobante_id'
    )
    comprobanteSerie = models.CharField(
        max_length=4,
        null=False,
        db_column='comprobante_serie',
        verbose_name='Serie del comprobante'
    )
    comprobanteNumero = models.IntegerField(
        db_column='comprobante_numero',
        verbose_name='Numero del comprobante',
        null=False
    )
    comprobanteTipo = models.IntegerField(
        db_column='comprobante_tipo',
        verbose_name='Tipo de Comprobante',
        null=False
    )
    comprobanteCliIdentificacion = models.CharField(
        max_length=11,
        verbose_name='Identificación del cliente',
        null=False,
        db_column='comprobante_identificacion'
    )
    comprobantePdf = models.TextField(
        db_column='comprobante_pdf',
        verbose_name='Pdf del comprobante'
    )
    comprobanteCdr = models.TextField(
        db_column='comprobante_cdr',
        verbose_name='Codigo de Respuesta del comprobante'
    )
    comprobanteXML = models.TextField(
        db_column='comprobante_xml',
        verbose_name='XML del comprobante',
        null=False
    )
    cabecera = models.OneToOneField(
        to=CabeceraComandaModel,
        db_column='cabecera_id',
        on_delete=models.CASCADE,
        related_name='comanda_cabecera',
        verbose_name='Comanda'
    )

    def __str__(self):
        return "%s %s" % (self.comprobanteSerie, self.comprobanteNumero)

    class Meta:
        db_table = 't_comprobante'
        verbose_name = 'Comprobante'
        verbose_name_plural = 'Comprobantes'


class DetalleComandaModel(models.Model):
    detalleId = models.AutoField(
        primary_key=True,
        db_column='detalle_id',
        null=False
    )
    detalleCantidad = models.IntegerField(
        db_column='detalle_cantidad',
        null=False,
        verbose_name='Cantidad'
    )
    detalleSubtotal = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=False,
        verbose_name='Subtotal inc IGV'
    )
    inventario = models.ForeignKey(
        to=InventarioModel,
        on_delete=models.PROTECT,
        verbose_name='Inventario',
        related_name='inventarioDetalles',
        db_column='inventario_id'
    )
    cabecera = models.ForeignKey(
        to=CabeceraComandaModel,
        on_delete=models.PROTECT,
        verbose_name='Cabecera',
        related_name='cabeceraDetalles',
        db_column='cabecera_id'
    )

    class Meta:
        db_table = 't_comanda_detalle'
        verbose_name = 'Detalle'
        verbose_name_plural = 'Detalles'
