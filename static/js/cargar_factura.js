function calcularProximoDia(diaSemana) {
    const hoy = new Date();
    const diaActual = hoy.getDay();
    let diferencia = diaSemana - diaActual;
    if (diferencia <= 0) diferencia += 7;
    const proxima = new Date(hoy);
    proxima.setDate(hoy.getDate() + diferencia);
    const anio = proxima.getFullYear();
    const mes = String(proxima.getMonth() + 1).padStart(2, '0');
    const dia = String(proxima.getDate()).padStart(2, '0');
    return `${anio}-${mes}-${dia}`;
}

function toggleNumeroCheque(selectId, boxId) {
    const select = document.getElementById(selectId);
    const box = document.getElementById(boxId);
    if (!select || !box) return;
    box.style.display = (select.value === 'Cheques / eCheqs') ? 'block' : 'none';
    if (select.value !== 'Cheques / eCheqs') {
        const input = box.querySelector('input[type="text"]');
        if (input) input.value = '';
    }
}

function setFechaPago(inputId, diaSemana) {
    const campo = document.getElementById(inputId);
    if (campo) campo.value = calcularProximoDia(diaSemana);
}

function cargarBancosPorSociedad() {
    const elSociedad = document.getElementById('select_sociedad');
    if (!elSociedad) return;

    const sociedadId = elSociedad.value;
    const selectBanco = document.getElementById('select_banco');

    if (!sociedadId) {
        selectBanco.innerHTML = '<option value="">Seleccionar Banco...</option>';
        return;
    }

    fetch('/obtener_bancos_sociedad/' + sociedadId)
        .then(response => response.json())
        .then(bancos => {
            selectBanco.innerHTML = '';
            if (bancos.length === 0) {
                selectBanco.innerHTML = '<option value="">Sin bancos registrados</option>';
                return;
            }
            if (bancos.length > 1) {
                selectBanco.innerHTML = '<option value="">Seleccionar Banco...</option>';
            }
            bancos.forEach(b => {
                const opt = document.createElement('option');
                opt.value = b.id;
                opt.textContent = b.nombre;
                if (bancos.length === 1) {
                    opt.selected = true;
                }
                selectBanco.appendChild(opt);
            });
        });
}

function obtenerFechaHoy() {
    const hoy = new Date();
    const anio = hoy.getFullYear();
    const mes = String(hoy.getMonth() + 1).padStart(2, '0');
    const dia = String(hoy.getDate()).padStart(2, '0');
    return `${anio}-${mes}-${dia}`;
}

document.addEventListener("DOMContentLoaded", function() {
    if (document.getElementById('select_sociedad') && document.getElementById('select_sociedad').value) {
        cargarBancosPorSociedad();
    }
    toggleNumeroCheque('select_forma_pago_manual', 'campo_num_cheque_manual');
    toggleNumeroCheque('select_forma_pago', 'campo_num_cheque_confirmar');

    // Predeterminar fecha de hoy si no está llena
    const fechaPagoManual = document.getElementById('fecha_pago_manual');
    if (fechaPagoManual && !fechaPagoManual.value) {
        fechaPagoManual.value = obtenerFechaHoy();
    }

    const fechaPagoConfirmar = document.getElementById('fecha_pago_confirmar');
    if (fechaPagoConfirmar && !fechaPagoConfirmar.value) {
        fechaPagoConfirmar.value = obtenerFechaHoy();
    }
});
