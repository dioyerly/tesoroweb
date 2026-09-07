function filtrarProveedores() {
    const texto = document.getElementById('buscador_proveedores').value.trim().toLowerCase();
    const filas = document.querySelectorAll('#tab-proveedores .fila-proveedor');
    let visibles = 0;

    filas.forEach(fila => {
        const nombre = fila.querySelector('input[name="nombre"]').value.toLowerCase();
        const cuit = fila.querySelector('input[name="cuit"]').value.toLowerCase();
        const coincide = nombre.includes(texto) || cuit.includes(texto);
        fila.style.display = coincide ? '' : 'none';
        if (coincide) visibles++;
    });

    const contador = document.getElementById('contador_proveedores');
    if (contador) contador.innerText = visibles;
}

function toggleCheckboxesProveedores(source) {
    document.querySelectorAll('.check_proveedor').forEach(cb => {
        cb.checked = source.checked;
    });
}

function eliminarProveedoresSeleccionados() {
    const seleccionados = [];
    document.querySelectorAll('.check_proveedor:checked').forEach(cb => {
        seleccionados.push(cb.value);
    });

    if (seleccionados.length === 0) {
        alert("Por favor seleccioná al menos un proveedor de la lista.");
        return;
    }

    const confirmacion = confirm(
        `¿Confirmás eliminar ${seleccionados.length} proveedor(es)? Esta acción no se puede deshacer.`
    );
    if (!confirmacion) return;

    fetch('/eliminar_proveedores_masivo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: seleccionados })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            window.location.reload();
        } else {
            alert("Ocurrió un error al eliminar los proveedores seleccionados.");
        }
    });
}


function cambiarPestana(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.btn-tab').forEach(el => el.classList.remove('active'));

    document.getElementById(tabId).style.display = 'block';

    if (tabId === 'tab-sociedades') document.getElementById('btn-tab-sociedades').classList.add('active');
    if (tabId === 'tab-proveedores') document.getElementById('btn-tab-proveedores').classList.add('active');
    if (tabId === 'tab-usuarios') document.getElementById('btn-tab-usuarios').classList.add('active');
    if (tabId === 'tab-admin') {
        document.getElementById('btn-tab-admin').classList.add('active');
        cargarMovimientos();
    }

    localStorage.setItem('pestana_activa', tabId);
}

let todosMovimientos = [];

function cargarMovimientos() {
    const tabla = document.getElementById('tablaMovimientos');
    if (!tabla) return;

    fetch('/api/movimientos_bancarios')
        .then(res => res.json())
        .then(data => {
            if (!Array.isArray(data) || data.length === 0) {
                tabla.innerHTML = '<tr><td colspan="5" style="padding: 20px; text-align: center; color: #8d99ae;">No hay movimientos</td></tr>';
                return;
            }

            todosMovimientos = data;
            mostrarMovimientos(data);
        })
        .catch(err => {
            console.error('Error cargando movimientos:', err);
            tabla.innerHTML = '<tr><td colspan="5" style="padding: 20px; text-align: center; color: red;">Error en la solicitud</td></tr>';
        });
}

function mostrarMovimientos(movimientos) {
    const tabla = document.getElementById('tablaMovimientos');

    if (!Array.isArray(movimientos) || movimientos.length === 0) {
        tabla.innerHTML = '<tr><td colspan="5" style="padding: 20px; text-align: center; color: #8d99ae;">No hay movimientos</td></tr>';
        return;
    }

    let html = '';
    for (let mov of movimientos) {
        try {
            const colorMonto = mov.monto > 0 ? '#2ec4b6' : '#ff6b9d';
            const colorTipo = mov.tipo === 'credito' ? '#2ec4b6' : '#ff6b9d';
            const montoFormato = Math.abs(mov.monto).toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            const desc = mov.descripcion ? mov.descripcion.substring(0, 40) : '';

            html += '<tr style="border-bottom: 1px solid #1e2139;">';
            html += '<td style="padding: 12px;"><input type="checkbox" class="checkbox-movimiento" value="' + mov.id + '" style="cursor: pointer;"></td>';
            html += '<td style="padding: 12px;">' + mov.fecha + '</td>';
            html += '<td style="padding: 12px; color: #8d99ae;">' + desc + '...</td>';
            html += '<td style="padding: 12px; text-align: right; color: ' + colorMonto + ';">$ ' + montoFormato + '</td>';
            html += '<td style="padding: 12px; text-align: center; color: ' + colorTipo + ';">' + mov.tipo + '</td>';
            html += '</tr>';
        } catch (e) {
            console.error('Error procesando movimiento:', mov, e);
        }
    }
    tabla.innerHTML = html;
    document.getElementById('selectAll').checked = false;
}

function filtrarPorFecha() {
    const desde = document.getElementById('filtroFechaDesde').value;
    const hasta = document.getElementById('filtroFechaHasta').value;

    if (!desde && !hasta) {
        alert('Selecciona al menos una fecha');
        return;
    }

    const filtrados = todosMovimientos.filter(mov => {
        const fecha = mov.fecha; // formato DD/MM/YYYY
        const [d, m, y] = fecha.split('/');
        const fechaMov = y + '-' + m + '-' + d; // convertir a YYYY-MM-DD

        let cumple = true;
        if (desde && fechaMov < desde) cumple = false;
        if (hasta && fechaMov > hasta) cumple = false;
        return cumple;
    });

    mostrarMovimientos(filtrados);
    document.getElementById('contadorFiltro').textContent = 'Mostrando: ' + filtrados.length + ' movimientos';
}

function limpiarFiltro() {
    document.getElementById('filtroFechaDesde').value = '';
    document.getElementById('filtroFechaHasta').value = '';
    document.getElementById('contadorFiltro').textContent = '';
    mostrarMovimientos(todosMovimientos);
}

function seleccionarTodos(checked) {
    document.querySelectorAll('.checkbox-movimiento').forEach(cb => cb.checked = checked);
}

function abrirModalBorrarSeleccionados() {
    const seleccionados = Array.from(document.querySelectorAll('.checkbox-movimiento:checked'));

    if (seleccionados.length === 0) {
        alert('Por favor selecciona al menos un movimiento');
        return;
    }

    const ids = seleccionados.map(cb => cb.value).join(',');
    document.getElementById('idsMovimientos').value = ids;
    document.getElementById('cantMovimientos').textContent = seleccionados.length;
    document.getElementById('modalBorrarSeleccionados').style.display = 'flex';
    document.querySelector('#modalBorrarSeleccionados input[name="confirmacion"]').value = '';
}

function abrirModalBorrarTodos() {
    document.getElementById('modalBorrarTodos').style.display = 'flex';
    document.querySelector('#modalBorrarTodos input[name="confirmacion"]').value = '';
}

function cerrarModal(idModal) {
    document.getElementById(idModal).style.display = 'none';
}

function confirmarBorrarSeleccionados() {
    const confirmacion = document.querySelector('#modalBorrarSeleccionados input[name="confirmacion"]').value;
    if (confirmacion !== 'CONFIRMO') {
        alert('Debes escribir "CONFIRMO" para confirmar');
        return;
    }

    const ids = document.getElementById('idsMovimientos').value;
    if (!ids) {
        alert('No hay movimientos seleccionados');
        return;
    }

    fetch('/borrar_movimientos_seleccionados', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirmacion: confirmacion, ids: ids })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            cerrarModal('modalBorrarSeleccionados');
            cargarMovimientos();
            alert('Movimientos eliminados correctamente');
        } else {
            alert('Error: ' + (data.message || 'No se pudo eliminar'));
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert('Error en la solicitud');
    });
}

function confirmarBorrarTodos() {
    const confirmacion = document.querySelector('#modalBorrarTodos input[name="confirmacion"]').value;
    if (confirmacion !== 'CONFIRMO') {
        alert('Debes escribir "CONFIRMO" para confirmar');
        return;
    }

    fetch('/limpiar_movimientos_bancarios', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirmacion: confirmacion })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            cerrarModal('modalBorrarTodos');
            cargarMovimientos();
            alert('Todos los movimientos han sido eliminados');
        } else {
            alert('Error: ' + (data.message || 'No se pudo eliminar'));
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert('Error en la solicitud');
    });
}

document.addEventListener("DOMContentLoaded", function() {
    let pestanaGuardada = localStorage.getItem('pestana_activa') || 'tab-sociedades';
    cambiarPestana(pestanaGuardada);
});
