// Dashboard: loader "sistema vivo" + graficos Chart.js con gradiente celeste-verde
(function () {
  function hideLoader() {
    var l = document.getElementById("pulse-loader");
    if (l) setTimeout(function () { l.classList.add("hidden-loader"); }, 700);
  }

  function gradient(ctx, area) {
    var g = ctx.createLinearGradient(0, area.top, 0, area.bottom);
    g.addColorStop(0, "rgba(56, 189, 248, 0.85)");
    g.addColorStop(1, "rgba(34, 197, 94, 0.35)");
    return g;
  }

  function toggleEmpty(canvasId, hasData) {
    var canvas = document.getElementById(canvasId);
    var empty = document.getElementById(canvasId + "-empty");
    if (!canvas || !empty) return;
    canvas.classList.toggle("d-none", !hasData);
    empty.classList.toggle("d-none", hasData);
  }

  async function initCharts() {
    var res = await fetch("/api/dashboard/stats");
    var data = await res.json();

    var hayCitas = data.citas.labels.length > 0;
    var hayEspecialidades = data.especialidades.labels.length > 0;
    var hayIngresos = data.ingresos.labels.length > 0;

    toggleEmpty("chartCitas", hayCitas);
    toggleEmpty("chartEspecialidades", hayEspecialidades);
    toggleEmpty("chartIngresos", hayIngresos);

    // Citas atendidas vs canceladas
    if (hayCitas) {
      new Chart(document.getElementById("chartCitas"), {
        type: "bar",
        data: {
          labels: data.citas.labels,
          datasets: [
            { label: "Atendidas", data: data.citas.atendidas, backgroundColor: "#22C55E", borderRadius: 6 },
            { label: "Canceladas", data: data.citas.canceladas, backgroundColor: "#94A3B8", borderRadius: 6 },
          ],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "bottom" } },
          scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } },
      });
    }

    // Especialidades mas demandadas
    if (hayEspecialidades) {
      new Chart(document.getElementById("chartEspecialidades"), {
        type: "doughnut",
        data: {
          labels: data.especialidades.labels,
          datasets: [{
            data: data.especialidades.data,
            backgroundColor: ["#38BDF8", "#22C55E", "#0EA5E9", "#4ADE80", "#94A3B8", "#7DD3FC"],
          }],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "right" } }, cutout: "62%" },
      });
    }

    // Ingresos por consultas
    if (hayIngresos) {
      new Chart(document.getElementById("chartIngresos"), {
        type: "line",
        data: {
          labels: data.ingresos.labels,
          datasets: [{
            label: "Ingresos",
            data: data.ingresos.data,
            fill: true,
            tension: 0.4,
            borderColor: "#0EA5E9",
            pointBackgroundColor: "#22C55E",
            backgroundColor: function (c) {
              var chart = c.chart;
              if (!chart.chartArea) return "rgba(56,189,248,0.2)";
              return gradient(chart.ctx, chart.chartArea);
            },
          }],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true } } },
      });
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    hideLoader();
    if (window.Chart) initCharts().catch(console.error);
  });
})();
