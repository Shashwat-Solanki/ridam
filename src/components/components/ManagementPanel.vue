<template>
  <div
    class="bg-light p-4 rounded shadow-sm"
    style="background-color: #1f2839"
    id="manag">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-start mb-2 small">
      <!-- View Entries -->
      <div class="mb-3">
        <div class="mb-1 fw-bold small text-dark">View Fields:</div>
        <div class="mb-2">
          <button class="btn btn-outline-dark btn-sm me-2">All</button>
          <button class="btn btn-outline-dark btn-sm" @click="addFieldOnly">
            +
          </button>
        </div>
        <div
          v-for="(entry, index) in viewEntries"
          :key="entry.id"
          class="d-flex align-items-center gap-2 mb-1 small text-dark">
          <select
            v-model="entry.field"
            @change="handleFieldChange"
            class="form-select form-select-sm w-auto text-dark">
            <option disabled value="">-- Field --</option>
            <option
              v-for="field in getAvailableFieldsForView(entry.field)"
              :key="field"
              :value="field">
              {{ field }}
            </option>
          </select>
          <button
            class="btn btn-sm btn-danger"
            @click="removeField(index, 'view')">
            &times;
          </button>
        </div>
      </div>

      <!-- Sort Entries -->
      <div class="mb-3">
        <div class="mb-1 fw-bold small text-dark">Sort Fields:</div>
        <div class="mb-2">
          <button class="btn btn-outline-dark btn-sm" @click="addFieldValue">
            +
          </button>
        </div>

        <div
          v-for="(entry, index) in sortEntries"
          :key="entry.id"
          class="sort-row d-flex align-items-center gap-2 mb-1 small text-dark">
          <select
            v-model="entry.field"
            @change="handleFieldChange"
            class="form-select form-select-sm w-auto text-dark">
            <option disabled value="">-- Field --</option>
            <option
              v-for="field in getAvailableFieldsForSort(entry.field)"
              :key="field"
              :value="field">
              {{ field }}
            </option>
          </select>

          <!-- Dynamic Inputs -->
          <template v-if="entry.field === 'Frequency'">
            <select
              v-model="entry.value"
              class="form-select form-select-sm w-auto text-dark">
              <option disabled value="">-- Select Frequency --</option>
              <option value="daily">daily</option>
              <option value="weekly">weekly</option>
              <option value="monthly">monthly</option>
            </select>
          </template>

          <template v-else-if="entry.field === 'Extension'">
            <input
              type="text"
              class="form-control form-control-sm w-auto text-dark"
              value=".tif"
              readonly
              disabled />
          </template>

          <template v-else-if="entry.field === 'Projections'">
            <select
              v-model="entry.value"
              class="form-select form-select-sm w-auto text-dark">
              <option disabled value="">-- Select Projection --</option>
              <option value="epsg:4326">EPSG:4326</option>
              <option value="3857">EPSG:3857</option>
            </select>
          </template>

          <template
            v-else-if="['Paused', 'RGB', 'Category'].includes(entry.field)">
            <select
              v-model="entry.value"
              class="form-select form-select-sm w-auto text-dark">
              <option disabled value="">-- Select --</option>
              <option value="true">True</option>
              <option value="false">False</option>
            </select>
          </template>

          <template v-else>
            <input
              v-model="entry.value"
              type="text"
              class="form-control form-control-sm w-auto text-dark"
              placeholder="Value" />
          </template>

          <button
            class="btn btn-sm btn-danger"
            @click="removeField(index, 'sort')">
            &times;
          </button>
        </div>
      </div>
    </div>

    <!-- Submit -->
    <div class="text-center mt-3">
      <button class="btn btn-primary" @click="handleSubmit">Submit</button>
    </div>

    <!-- Display Table Results -->
    <div
      v-if="queryResults.length === 0"
      class="bg-secondary bg-opacity-10 p-5 text-muted text-center mt-4 rounded small">
      Tables will be displayed here
    </div>

    <div v-else class="table-responsive mt-4">
      <table
        class="table table-bordered table-sm table-striped small text-dark">
        <thead class="table-light">
          <tr>
            <th v-for="(value, key) in queryResults[0]" :key="key">
              {{ key }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in queryResults" :key="index">
            <td v-for="(value, key) in row" :key="key">{{ value }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

const allFields = [
  "Name",
  "Frequency",
  "Extension",
  "Projections",
  "Paused",
  "RGB",
  "Category",
  "Band Info",
  "Aux Data",
  "Tags",
  "Theme ID",
  "Sub-Theme ID",
  "Location",
  "City",
  "Contact Person",
  "Organization",
  "Mailing Address",
  "Country",
  "Contact Telephone",
];

const viewEntries = ref([]);
const sortEntries = ref([]);
const queryResults = ref([]);
let idCounter = 0;

function addFieldOnly() {
  viewEntries.value.push({ id: idCounter++, field: "" });
}

function addFieldValue() {
  sortEntries.value.push({ id: idCounter++, field: "", value: "" });
}

function removeField(index, type) {
  if (type === "view") {
    viewEntries.value.splice(index, 1);
  } else {
    sortEntries.value.splice(index, 1);
  }
}

function getAvailableFieldsForView(currentField) {
  const selected = viewEntries.value
    .map((e) => e.field)
    .filter((f) => f && f !== currentField);
  return allFields.filter((f) => !selected.includes(f));
}

function getAvailableFieldsForSort(currentField) {
  const selected = sortEntries.value
    .map((e) => e.field)
    .filter((f) => f && f !== currentField);
  return allFields.filter((f) => !selected.includes(f));
}

function handleFieldChange() {
  viewEntries.value = [...viewEntries.value];
  sortEntries.value = [...sortEntries.value];
}

async function handleSubmit() {
  try {
    const response = await fetch("http://127.0.0.1:5000", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        type: "manage",
        viewEntries: viewEntries.value,
        sortEntries: sortEntries.value,
      }),
    });

    const result = await response.json();
    if (result.status === "success") {
      queryResults.value = result.data;
    } else {
      throw new Error(result.message);
    }
  } catch (err) {
    console.error("Fetch error:", err);
    alert("Error occurred during data fetching");
  }
}
</script>
<style scoped>
/* minimal tweaks */
#manag {
  height: 82vh;
  overflow-y: auto;
}

@media (max-width: 767px) {
  #manag {
    height: 62vh;
  }
}
</style>
