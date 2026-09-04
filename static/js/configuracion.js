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

    localStorage.setItem('pestana_activa', tabId);
}

document.addEventListener("DOMContentLoaded", function() {
    let pestanaGuardada = localStorage.getItem('pestana_activa') || 'tab-sociedades';
    cambiarPestana(pestanaGuardada);
});
