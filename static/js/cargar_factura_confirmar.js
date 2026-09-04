document.getElementById('nombre_emisor_editable').addEventListener('input', function() {
    const valor = this.value.trim();
    const datalist = document.getElementById('lista_proveedores_datalist');
    const badge = document.getElementById('badge_estado_proveedor');
    if (!datalist) return;

    const opcion = Array.from(datalist.options).find(
        opt => opt.value.toLowerCase() === valor.toLowerCase()
    );

    if (opcion) {
        document.getElementById('cuit_emisor_editable').value = opcion.dataset.cuit || '';
        document.getElementById('cbu_rapido').value = opcion.dataset.cbu || '';
        document.getElementById('input_proveedor_id').value = opcion.dataset.id || '';
        if (badge) {
            badge.innerHTML = '<span style="background: rgba(40, 167, 69, 0.2); color: #28a745; border: 1px solid #28a745; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; display: inline-block;">✓ Registrado en Base</span>';
        }
    } else {
        document.getElementById('input_proveedor_id').value = '';
        if (badge) {
            badge.innerHTML = '<span style="background: rgba(255, 193, 7, 0.2); color: #ffc107; border: 1px solid #ffc107; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; display: inline-block;">⚠️ Nuevo / No Guardado</span>';
        }
    }
});


document.getElementById("form_confirmar_pago").addEventListener("submit", function(e) {
    // 1. Copiar los valores actualizados de la caja de pre-validación superior
    const inputEmisorVisible = document.getElementById("nombre_emisor_editable"); // Input visible del emisor
    const inputCuitVisible = document.getElementById("cuit_emisor_editable");     // Input visible del CUIT
    const inputCbuVisible = document.getElementById("cbu_rapido");                // Input visible del CBU

    if (inputEmisorVisible) document.getElementById("hidden_emisor_nombre").value = inputEmisorVisible.value.trim();
    if (inputCuitVisible) document.getElementById("hidden_emisor_cuit").value = inputCuitVisible.value.trim();
    if (inputCbuVisible) document.getElementById("hidden_cbu_alias").value = inputCbuVisible.value.trim();

    const tipoGasto = document.getElementById("select_tipo_gasto").value;
    const emisorNombre = document.getElementById("hidden_emisor_nombre").value;
    const emisorCuit = document.getElementById("hidden_emisor_cuit").value;

    // 2. Bloqueo en Frontend si falta emisor en gastos de proveedor
    if (tipoGasto === 'proveedor') {
        if (!emisorNombre || emisorNombre.length < 3) {
            e.preventDefault();
            alert("⚠️ No se puede programar el pago: Ingrese un Nombre de Proveedor válido en el panel superior.");
            return false;
        }
        if (!emisorCuit || emisorCuit.length < 10) {
            e.preventDefault();
            alert("⚠️ No se puede programar el pago: Ingrese un CUIT válido para el proveedor.");
            return false;
        }
    }
});


document.getElementById('cuit_emisor_editable').addEventListener('blur', function() {
    const cuit = this.value.trim();
    if (!cuit || cuit.length < 10) return;

    fetch('/buscar_proveedor_por_cuit/' + encodeURIComponent(cuit))
        .then(res => res.json())
        .then(data => {
            const badge = document.getElementById('badge_estado_proveedor');
            if (data.encontrado) {
                document.getElementById('nombre_emisor_editable').value = data.nombre;
                document.getElementById('cbu_rapido').value = data.cbu_alias;
                document.getElementById('input_proveedor_id').value = data.id;
                if (badge) {
                    badge.innerHTML = '<span style="background: rgba(40, 167, 69, 0.2); color: #28a745; border: 1px solid #28a745; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; display: inline-block;">✓ Registrado en Base</span>';
                }
            } else {
                document.getElementById('input_proveedor_id').value = '';
                if (badge) {
                    badge.innerHTML = '<span style="background: rgba(255, 193, 7, 0.2); color: #ffc107; border: 1px solid #ffc107; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; display: inline-block;">⚠️ Nuevo / No Guardado</span>';
                }
            }
        });
});


function guardarProveedorRapido() {
    const nombreCorr = document.getElementById('nombre_emisor_editable').value;
    const cuitCorr = document.getElementById('cuit_emisor_editable').value.trim();
    const cbu = document.getElementById('cbu_rapido').value;

    fetch('/guardar_proveedor_rapido_ajax', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            cuit: cuitCorr,
            nombre: nombreCorr,
            cbu_alias: cbu
        })
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'ok') {
            document.getElementById('input_proveedor_id').value = data.id;

            // Actualización de estado en pantalla
            const badge = document.getElementById('badge_estado_proveedor');
            if (badge) {
                badge.innerHTML = '<span style="background: rgba(40, 167, 69, 0.2); color: #28a745; border: 1px solid #28a745; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; display: inline-block;">✓ Registrado en Base</span>';
            }

            // Notificación Flotante Profesional (Toast)
            mostrarNotificacionFlotante('Emisor registrado correctamente: ' + nombreCorr);
        }
    });
}

// Función generadora de notificaciones flotantes
function mostrarNotificacionFlotante(mensaje) {
    const toast = document.createElement('div');
    toast.textContent = mensaje;
    toast.style.cssText = `
        position: fixed;
        bottom: 25px;
        right: 25px;
        background: rgba(40, 167, 69, 0.95);
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.9rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        border: 1px solid #28a745;
        z-index: 9999;
        transition: opacity 0.4s ease, transform 0.4s ease;
        opacity: 0;
        transform: translateY(10px);
    `;

    document.body.appendChild(toast);

    // Animación de entrada
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    }, 50);

    // Desvanecimiento y descarte automático a los 3.5 segundos
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 400);
    }, 3500);
}
