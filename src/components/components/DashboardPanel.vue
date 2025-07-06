<template>
  <div
    class="bg-light p-3 rounded shadow-sm"
    style="background: #1f2839"
    id="bod">
    <!-- Last‑10 table with total datasets count together -->
    <div class="card shadow-sm mb-4">
      <div class="card-body p-3">
        <h6 class="card-title mb-2 fw-normal">
          Last 10 Datasets <small class="text-muted">(key columns)</small>
        </h6>
        <div
          class="table-responsive"
          style="max-height: 55vh; overflow-y: auto">
          <table
            class="table table-sm table-striped small align-middle text-light">
            <thead class="table-light text-dark">
              <tr>
                <th v-for="c in columns" :key="c">{{ c }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="d in lastTen" :key="d.id">
                <td v-for="c in columns" :key="c">{{ formatCell(d[c], c) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="d-flex justify-content-between align-items-center mt-2">
          <h6 class="mb-0 text-dark">Total Entries</h6>
          <h5 class="mb-0 fw-bold text-dark">{{ stats.totalEntries }}</h5>
        </div>
      </div>
    </div>

    <!-- Charts row -->
    <div class="row gy-3">
      <div class="col-12 col-lg-8">
        <highcharts :options="dailyLineOptions" />
      </div>
      <div class="col-12 col-lg-4">
        <highcharts :options="poolPieOptions" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import Highcharts from "highcharts";
import HighchartsVue from "highcharts-vue";
Highcharts.setOptions({ lang: { numericSymbols: null, locale: "en-US" } });

export default {
  name: "DashboardPanel",
  components: { highcharts: HighchartsVue.component },
  setup() {
    const stats = ref({ totalEntries: 0 });
    const lastTen = ref([]);
    const dailyLineOptions = ref({});
    const poolPieOptions = ref({});

    const columnsWanted = [
      "name",
      "frequency",
      "projections",
      "extension",
      "pyramid_id",
      "theme_id",
    ];
    const columns = computed(() =>
      lastTen.value.length
        ? columnsWanted.filter((c) => c in lastTen.value[0])
        : []
    );

    const formatCell = (v, c) => {
      if (v == null) return "-";
      if (c === "tags" && Array.isArray(v)) return v.join(", ");
      if (typeof v === "boolean") return v ? "Yes" : "No";
      if (typeof v === "object") return JSON.stringify(v);
      return v;
    };

    const buildDailyLine = (ec) => {
      const days = Object.keys(ec).sort();
      dailyLineOptions.value = {
        chart: { type: "line", backgroundColor: "transparent" },
        title: { text: "Entries – last 30 days", style: { color: "#fff" } },
        xAxis: { categories: days, labels: { style: { color: "#ddd" } } },
        yAxis: {
          title: { text: "Entries", style: { color: "#ddd" } },
          labels: { style: { color: "#ddd" } },
          allowDecimals: false,
        },
        series: [
          { name: "Entries", data: days.map((d) => ec[d]), color: "#0d6efd" },
        ],
        tooltip: { pointFormat: "<b>{point.y}</b> entries" },
        legend: { enabled: false },
      };
    };

    const buildPoolPie = (pc) => {
      poolPieOptions.value = {
        chart: { type: "pie", backgroundColor: "transparent" },
        title: { text: "Pools", style: { color: "#fff" } },
        plotOptions: {
          pie: {
            dataLabels: {
              color: "#fff",
              formatter() {
                return this.point.name;
              },
            },
          },
        },
        series: [
          {
            name: "Datasets",
            data: Object.entries(pc).map(([p, c]) => ({
              name: p || "Unknown",
              y: c,
            })),
          },
        ],
        tooltip: { pointFormat: "<b>{point.y}</b> datasets" },
      };
    };

    const fetchDashboard = async () => {
      try {
        const r = await fetch("http://127.0.0.1:5000/", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ type: "dashboard" }),
        });
        if (!r.ok) throw new Error("HTTP " + r.status);
        const j = await r.json();
        if (j.status !== "success") throw new Error(j.msg || "API error");
        stats.value.totalEntries = j.totalEntries ?? 0;
        lastTen.value = j.last10Datasets ?? [];
        buildDailyLine(j.dailyEntryCounts ?? {});
        buildPoolPie(j.poolCounts ?? {});
      } catch (e) {
        console.error("Dashboard fetch error", e);
      }
    };

    onMounted(fetchDashboard);

    return {
      stats,
      lastTen,
      columns,
      formatCell,
      dailyLineOptions,
      poolPieOptions,
    };
  },
};
</script>

<style scoped>
#bod {
  height: 75dvh;
  overflow-y: auto;
  color: #e9ecef;
}
@media (max-width: 767px) {
  #bod {
    height: 62vh;
  }
}
thead th {
  position: sticky;
  top: 0;
  background: #f8f9fa;
  z-index: 10;
}
</style>
