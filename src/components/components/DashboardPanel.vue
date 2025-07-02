<template>
  <div
    class="bg-light p-4 rounded shadow-sm"
    style="background-color: #1f2839"
    id="bod">
    <!-- Total datasets -->
    <div class="card shadow-sm mb-4">
      <div class="card-body text-center">
        <h5 class="card-title mb-3">Total Datasets</h5>
        <h1 class="display-5 fw-bold">{{ stats.totalTables }}</h1>
      </div>
    </div>

    <!-- Last 10 datasets table -->
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <h5 class="card-title mb-3">Last 10 Datasets</h5>
        <div
          class="table-responsive"
          style="max-height: 60vh; overflow-y: auto">
          <table class="table table-sm table-striped small align-middle">
            <thead class="table-light">
              <tr>
                <th v-for="col in columns" :key="col">{{ col }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="d in lastTen" :key="d.id">
                <td v-for="col in columns" :key="col">
                  {{ formatCell(d[col], col) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="row gy-4">
      <!-- Frequency Bar Chart -->
      <div class="col-12 col-lg-6">
        <highcharts :options="frequencyBarOptions" />
      </div>

      <!-- Themes Pie Chart -->
      <div class="col-12 col-lg-6">
        <highcharts :options="themePieOptions" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from "vue";
import HighchartsVue from "highcharts-vue";

export default {
  name: "DashboardPanel",
  components: { highcharts: HighchartsVue.component },
  setup() {
    const stats = ref({ totalTables: 0 });
    const lastTen = ref([]);
    const frequencyBarOptions = ref({});
    const themePieOptions = ref({});

    const columnsOrder = [
      "name",
      "frequency",
      "extension",
      "projections",
      "paused",
      "rgb",
      "category",
      "band_info",
      "aux_data",
      "tags",
      "theme_id",
      "sub_theme_id",
      "location",
      "city",
      "contact_person",
      "organization",
      "mailing_address",
      "country",
      "contact_telephone",
    ];

    const columns = computed(() => {
      if (!lastTen.value.length) return [];
      return columnsOrder.filter((c) =>
        Object.keys(lastTen.value[0]).includes(c)
      );
    });

    function formatCell(val, col) {
      if (val === null || val === undefined) return "-";
      if (col === "tags" && Array.isArray(val)) return val.join(", ");
      if (typeof val === "boolean") return val ? "Yes" : "No";
      if (typeof val === "object") return JSON.stringify(val);
      return val;
    }

    async function fetchAll() {
      const res = await fetch("http://127.0.0.1:5000/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type: "dashboard" }),
      });
      const data = await res.json();
      if (data.status !== "success") throw new Error(data.message);

      stats.value = { totalTables: data.totalTables };
      lastTen.value = data.last10Datasets;
      buildFrequencyChart(data.frequencyCounts || {});
      buildThemePieChart(data.themeCounts || {});
    }

    function buildFrequencyChart(freq) {
      const cats = Object.keys(freq);
      const vals = Object.values(freq);
      frequencyBarOptions.value = {
        chart: { type: "column" },
        title: { text: "Frequency" },
        lang: { numericSymbols: null, locale: "en" },
        xAxis: { categories: cats, title: { text: "Frequency" } },
        yAxis: { allowDecimals: false, title: { text: "Datasets" } },
        series: [{ name: "Datasets", data: vals }],
        tooltip: { pointFormat: "<b>{point.y}</b> datasets" },
      };
    }

    function buildThemePieChart(themeCnt) {
      const sData = Object.entries(themeCnt).map(([k, v]) => ({
        name: k || "Unknown",
        y: v,
      }));
      themePieOptions.value = {
        chart: { type: "pie" },
        title: { text: "Themes" },
        lang: { numericSymbols: null, locale: "en" },
        plotOptions: {
          pie: {
            dataLabels: {
              formatter() {
                return this.point.name;
              },
            },
          },
        },
        series: [{ name: "Themes", data: sData }],
        tooltip: { pointFormat: "<b>{point.y}</b> datasets" },
      };
    }

    onMounted(fetchAll);
    return {
      stats,
      lastTen,
      columns,
      formatCell,
      frequencyBarOptions,
      themePieOptions,
    };
  },
};
</script>

<style scoped>
#bod {
  height: 82vh;
  overflow-y: auto;
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
