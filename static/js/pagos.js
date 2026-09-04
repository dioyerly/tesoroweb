function descargarExcelFiltrado(incluirTodo) {
    const sociedadId = document.getElementById('filtro_sociedad').value;
    let fechaPago = document.getElementById('filtro_fecha').value;
    const formaPago = document.getElementById('filtro_forma_pago').value;

    // Si no especificó fecha, usar hoy
    if (!fechaPago) {
        const hoy = new Date();
        const anio = hoy.getFullYear();
        const mes = String(hoy.getMonth() + 1).padStart(2, '0');
        const dia = String(hoy.getDate()).padStart(2, '0');
        fechaPago = `${anio}-${mes}-${dia}`;
    }

    let url = '/exportar_excel?sociedad_id=' + sociedadId + '&fecha_pago=' + fechaPago + '&forma_pago=' + encodeURIComponent(formaPago);
    if (incluirTodo) {
        url += '&incluir_pagados=true';
    }
    window.location.href = url;
}

function toggleCheckboxes(source) {
    const checkboxes = document.getElementsByClassName('check_pago');
    for(let i = 0; i < checkboxes.length; i++) {
        checkboxes[i].checked = source.checked;
    }
}

function marcarIndividualPagado(pagoId) {
    fetch('/marcar_pagado_masivo', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ids: [pagoId]})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            window.location.reload();
        }
    });
}

function marcarComoPendiente(pagoId) {
    fetch('/marcar_como_pendiente', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({pago_id: pagoId})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            window.location.reload();
        } else {
            alert('Error: ' + (data.message || 'Error desconocido'));
        }
    });
}

function marcarSeleccionadosComoPagados() {
    const seleccionados = [];
    document.querySelectorAll('.check_pago:checked').forEach(cb => {
        seleccionados.push(cb.value);
    });

    if (seleccionados.length === 0) {
        alert("Por favor selecciona al menos un pago pendiente de la lista.");
        return;
    }

    const payload = { ids: seleccionados };

    fetch('/marcar_pagado_masivo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            window.location.reload();
        }
    });
}
function eliminarSeleccionados() {
    const seleccionados = [];
    document.querySelectorAll('.check_pago:checked').forEach(cb => {
        seleccionados.push(cb.value);
    });

    if (seleccionados.length === 0) {
        alert("Por favor selecciona al menos un pago de la lista.");
        return;
    }

    const confirmacion1 = confirm(
        `¿Confirmás eliminar ${seleccionados.length} pago(s)? Esta acción no se puede deshacer.`
    );
    if (!confirmacion1) return;

    const confirmacion2 = confirm(
        "Última confirmación: los pagos seleccionados se van a borrar definitivamente. ¿Continuar?"
    );
    if (!confirmacion2) return;

    const payload = { ids: seleccionados };

    fetch('/eliminar_pago_masivo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            window.location.reload();
        } else {
            alert("Ocurrió un error al eliminar los pagos seleccionados.");
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.btn-edit-cbu').forEach(btn => {
        btn.addEventListener('click', function() {
            const pagoId = this.dataset.pagoId;
            document.getElementById('cbu_display_' + pagoId).style.display = 'none';
            document.getElementById('cbu_edit_' + pagoId).style.display = 'block';
            document.getElementById('cbu_input_' + pagoId).focus();
        });
    });

    document.querySelectorAll('.btn-cancelar-cbu').forEach(btn => {
        btn.addEventListener('click', function() {
            const pagoId = this.dataset.pagoId;
            document.getElementById('cbu_display_' + pagoId).style.display = 'inline';
            document.getElementById('cbu_edit_' + pagoId).style.display = 'none';
        });
    });

    document.querySelectorAll('.btn-guardar-cbu').forEach(btn => {
        btn.addEventListener('click', function() {
            const pagoId = this.dataset.pagoId;
            const proveedorId = this.dataset.proveedorId;
            const nuevoCbu = document.getElementById('cbu_input_' + pagoId).value.trim();

            fetch('/actualizar_cbu_proveedor/' + proveedorId, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cbu_alias: nuevoCbu })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'ok') {
                    const displayCbu = document.querySelector('#cbu_display_' + pagoId + ' span:nth-child(2)');
                    if (displayCbu) {
                        displayCbu.textContent = nuevoCbu || '(vacío)';
                    }
                    document.getElementById('cbu_display_' + pagoId).style.display = 'inline';
                    document.getElementById('cbu_edit_' + pagoId).style.display = 'none';
                } else {
                    alert('Error al guardar el CBU: ' + data.message);
                }
            })
            .catch(err => alert('Error: ' + err));
        });
    });
});
