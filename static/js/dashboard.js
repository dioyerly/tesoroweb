let fechaActual = new Date();
let fechaSeleccionadaStr = "";
let pagosDelMes = {};

const nombresMeses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"];

function cargarPagosDelMes(callback) {
    const año = fechaActual.getFullYear();
    const mes = fechaActual.getMonth() + 1;
    fetch(`/obtener_pagos_mes/${año}/${mes}`)
    .then(res => res.json())
    .then(data => {
        pagosDelMes = data;
        if (callback) callback();
    })
    .catch(() => {
        pagosDelMes = {};
        if (callback) callback();
    });
}

function renderizarCalendario() {
    const año = fechaActual.getFullYear();
    const mes = fechaActual.getMonth();

    document.getElementById("titulo_mes").innerText = `${nombresMeses[mes]} ${año}`;

    const primerDia = new Date(año, mes, 1).getDay();
    const ultimoDia = new Date(año, mes + 1, 0).getDate();

    const grid = document.getElementById("grid_dias");
    grid.innerHTML = "";

    for (let i = 0; i < primerDia; i++) {
        grid.innerHTML += `<div></div>`;
    }

    const hoyObj = new Date();

    for (let dia = 1; dia <= ultimoDia; dia++) {
        const diaPadded = String(dia).padStart(2, '0');
        const mesPadded = String(mes + 1).padStart(2, '0');
        const fechaIso = `${año}-${mesPadded}-${diaPadded}`;

        let clases = "dia-cal";
        if (dia === hoyObj.getDate() && mes === hoyObj.getMonth() && año === hoyObj.getFullYear()) {
            clases += " hoy";
        }
        if (fechaIso === fechaSeleccionadaStr) {
            clases += " seleccionado";
        }

        let indicador = "";
        let tituloTip = "";
        if (pagosDelMes[fechaIso]) {
            const info = pagosDelMes[fechaIso];
            tituloTip = `title="${info.cantidad} pago(s) - $ ${info.monto.toFixed(2)}"`;
            indicador = '<span class="punto-pago"></span>';
        }

        grid.innerHTML += `<div class="${clases}" ${tituloTip} onclick="seleccionarDia('${fechaIso}', '${diaPadded}/${mesPadded}/${año}')">${dia}${indicador}</div>`;
    }
}

function cambiarMes(delta) {
    fechaActual.setMonth(fechaActual.getMonth() + delta);
    cargarPagosDelMes(renderizarCalendario);
}

function seleccionarDia(fechaIso, fechaFormateada) {
    fechaSeleccionadaStr = fechaIso;
    document.querySelectorAll(".txt_fecha_sel").forEach(el => el.innerText = fechaFormateada);
    renderizarCalendario();
    cargarMetricasyRecordatorios();
}

function cargarMetricasyRecordatorios() {
    if (!fechaSeleccionadaStr) return;

    // 1. Cargar Métricas Dinámicas de la fecha seleccionada
    fetch(`/obtener_metricas_dia/${fechaSeleccionadaStr}`)
    .then(res => res.json())
    .then(data => {
        if(!data.error) {
            document.getElementById("card_cant_hoy").innerText = data.cant_pendientes_dia;
            document.getElementById("card_monto_hoy").innerText = "$ " + data.monto_dia.toFixed(2);
            document.getElementById("card_vencen_pronto").innerText = data.cant_vencen_7_dias;
            document.getElementById("card_monto_vencen_pronto").innerText = "($ " + data.monto_vencen_7_dias.toFixed(2) + ")";
        }
    });

    // 2. Cargar Recordatorios de la fecha seleccionada
    fetch(`/obtener_recordatorios/${fechaSeleccionadaStr}`)
    .then(res => res.json())
    .then(data => {
        const lista = document.getElementById("lista_recordatorios");
        lista.innerHTML = "";

        if (!data || data.length === 0) {
            lista.innerHTML = `<li style="color: var(--text-muted); font-size: 0.85rem;">Sin recordatorios para este día.</li>`;
            return;
        }

        data.forEach(item => {
            const colorTexto = item.hecho ? 'var(--text-muted)' : (item.atrasado ? '#dc3545' : 'white');
            const tachado = item.hecho ? 'line-through' : 'none';
            const badgeAtrasado = (item.atrasado && !item.hecho)
                ? `<span style="background: rgba(220,53,69,0.2); color: #dc3545; border: 1px solid #dc3545; padding: 1px 6px; border-radius: 4px; font-size: 0.65rem; font-weight: bold; margin-left: 6px; white-space: nowrap;">ATRASADA (${item.fecha})</span>`
                : '';

            lista.innerHTML += `
                <li style="display: flex; justify-content: space-between; align-items: center; gap: 8px; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.85rem;">
                    <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; flex-grow: 1; min-width: 0;">
                        <input type="checkbox" ${item.hecho ? 'checked' : ''} onchange="toggleRecordatorio(${item.id}, this.checked)" style="flex-shrink: 0; width: 16px; height: 16px; cursor: pointer;">
                        <span style="color: ${colorTexto}; text-decoration: ${tachado}; overflow-wrap: anywhere;">${item.nota}</span>
                    </label>
                    <div style="display: flex; align-items: center; flex-shrink: 0;">
                        ${badgeAtrasado}
                        <button onclick="eliminarRecordatorio(${item.id})" style="background: none; border: none; color: #dc3545; cursor: pointer; margin-left: 6px;">❌</button>
                    </div>
                </li>
            `;
        });
    });
}

function agregarRecordatorio() {
    const input = document.getElementById("input_nota");
    const nota = input.value.trim();
    const recurrencia = document.getElementById("select_recurrencia").value;

    if (!fechaSeleccionadaStr) {
        alert("Por favor selecciona un día del calendario.");
        return;
    }
    if (!nota) return;

    fetch('/guardar_recordatorio', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({fecha: fechaSeleccionadaStr, nota: nota, recurrencia: recurrencia})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            input.value = "";
            document.getElementById("select_recurrencia").value = "unica";
            cargarPagosDelMes(renderizarCalendario);
            cargarMetricasyRecordatorios();
        } else {
            alert("Error al guardar: " + (data.message || "Error desconocido"));
        }
    });
}

function toggleRecordatorio(id, hecho) {
    fetch(`/marcar_recordatorio/${id}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({hecho: hecho})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            cargarMetricasyRecordatorios();
        }
    });
}

function eliminarRecordatorio(id) {
    fetch(`/eliminar_recordatorio/${id}`, {method: 'POST'})
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            cargarMetricasyRecordatorios();
        }
    });
}

document.addEventListener("DOMContentLoaded", function() {
    const hoy = new Date();
    const diaPadded = String(hoy.getDate()).padStart(2, '0');
    const mesPadded = String(hoy.getMonth() + 1).padStart(2, '0');
    const fechaIso = `${hoy.getFullYear()}-${mesPadded}-${diaPadded}`;

    cargarPagosDelMes(function() {
        seleccionarDia(fechaIso, `${diaPadded}/${mesPadded}/${hoy.getFullYear()}`);
    });
});
