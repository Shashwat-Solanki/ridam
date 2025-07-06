<template>
  <div
    class="bg-light p-4 rounded shadow-sm"
    style="background-color: #1f2839"
    id="manag">
    <!-- ── controls row ── -->
    <div class="d-flex justify-content-between align-items-start mb-2 small">
      <!-- View fields -->
      <div class="mb-3">
        <div class="fw-bold small text-dark mb-1">View Fields:</div>
        <div class="mb-2">
          <button
            class="btn btn-outline-dark btn-sm me-2"
            @click="viewEntries = []">
            All
          </button>
          <button class="btn btn-outline-dark btn-sm" @click="addFieldOnly">
            +
          </button>
        </div>

        <div
          v-for="(entry, idx) in viewEntries"
          :key="entry.id"
          class="d-flex align-items-center gap-2 mb-1 text-dark">
          <select
            v-model="entry.field"
            @change="handleFieldChange"
            class="form-select form-select-sm w-auto text-dark">
            <option disabled value="">-- Field --</option>
            <option
              v-for="f in getAvailableFieldsForView(entry.field)"
              :key="f"
              :value="f">
              {{ f }}
            </option>
          </select>
          <button
            class="btn btn-sm btn-danger"
            @click="removeField(idx, 'view')">
            ×
          </button>
        </div>
      </div>

      <!-- Sort fields -->
      <div class="mb-3">
        <div class="fw-bold small text-dark mb-1">Sort Fields:</div>
        <div class="mb-2">
          <button class="btn btn-outline-dark btn-sm" @click="addFieldValue">
            +
          </button>
        </div>

        <div
          v-for="(entry, idx) in sortEntries"
          :key="entry.id"
          class="d-flex align-items-center gap-2 mb-1 text-dark">
          <select
            v-model="entry.field"
            @change="handleFieldChange"
            class="form-select form-select-sm w-auto text-dark">
            <option disabled value="">-- Field --</option>
            <option
              v-for="f in getAvailableFieldsForSort(entry.field)"
              :key="f"
              :value="f">
              {{ f }}
            </option>
          </select>

          <!-- Dynamic value input -->
          <template v-if="entry.field === 'Frequency'">
            <select
              v-model="entry.value"
              class="form-select form-select-sm w-auto text-dark">
              <option disabled value="">-- Select --</option>
              <option value="daily">daily</option>
              <option value="weekly">weekly</option>
              <option value="monthly">monthly</option>
            </select>
          </template>

          <template v-else-if="entry.field === 'Extension'">
            <input
              class="form-control form-control-sm w-auto text-dark"
              value=".tif"
              readonly
              disabled />
          </template>

          <template v-else-if="entry.field === 'Projections'">
            <select
              v-model="entry.value"
              class="form-select form-select-sm w-auto text-dark">
              <option disabled value="">-- Select --</option>
              <option value="EPSG:4326">EPSG:4326</option>
              <option value="EPSG:3857">EPSG:3857</option>
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
              class="form-control form-control-sm w-auto text-dark"
              placeholder="Value" />
          </template>

          <button
            class="btn btn-sm btn-danger"
            @click="removeField(idx, 'sort')">
            ×
          </button>
        </div>
      </div>
    </div>

    <!-- Submit (still here if user wants to refresh manually) -->
    <div class="text-center mt-3">
      <button class="btn btn-primary" @click="handleSubmit">Submit</button>
    </div>

    <!-- Results -->
    <div
      v-if="queryResults.length === 0"
      class="bg-secondary bg-opacity-10 p-5 text-muted text-center mt-4 rounded small">
      Tables will be displayed here
    </div>

    <div
      v-else
      class="table-wrapper mt-4"
      style="max-height: 450px; overflow: auto">
      <table
        class="table table-bordered table-sm table-striped small text-dark"
        style="min-width: 900px">
        <thead class="table-light">
          <tr>
            <th v-for="(v, k) in queryResults[0]" :key="k">{{ k }}</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, i) in queryResults" :key="i">
            <td v-for="(v, k) in row" :key="k">
              <template v-if="editIndex === i">
                <textarea
                  v-if="k === 'metadata'"
                  v-model="editedRow[k]"
                  rows="4"
                  class="form-control form-control-sm"
                  style="
                    font-family: monospace;
                    white-space: pre-wrap;
                  "></textarea>
                <input
                  v-else
                  v-model="editedRow[k]"
                  class="form-control form-control-sm" />
              </template>
              <template v-else>
                {{ k === "metadata" ? JSON.stringify(v) : v }}
              </template>
            </td>
            <td>
              <template v-if="editIndex === i">
                <button
                  class="btn btn-sm btn-success me-1"
                  @click="saveEdit(i)">
                  Save
                </button>
                <button
                  class="btn btn-sm btn-secondary me-1"
                  @click="cancelEdit">
                  Cancel
                </button>
                <button
                  class="btn btn-sm btn-danger"
                  @click="deleteDataset(editedRow.id)">
                  Delete
                </button>
              </template>
              <template v-else>
                <button
                  class="btn btn-sm btn-primary me-2"
                  @click="startEdit(i)">
                  Edit
                </button>
                <button
                  class="btn btn-sm btn-danger"
                  @click="deleteDataset(row.id)">
                  Delete
                </button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

/* ---------- fields list ---------- */
const allFields = [
  "ID",
  "Name",
  "Frequency",
  "Extension",
  "Projections",
  "Paused",
  "RGB",
  "Category",
  "Band Info",
  "Aux Data",
  "Remarks",
  "Tags",
  "Theme ID",
  "Sub-Theme ID",
  "Product ID",
  "Base Path",
  "Create Directory",
  "Pyramid ID",
  "From Time",
  "To Time",
  "Pool",
  "Location",
  "City",
  "Contact Person",
  "Organization",
  "Mailing Address",
  "Country",
  "Contact Telephone",
];

/* ---------- reactive state ---------- */
const viewEntries = ref([]);
const sortEntries = ref([]);
const queryResults = ref([]);
let idCounter = 0;

/* ---------- editing state ---------- */
const editIndex = ref(-1);
const editedRow = ref({});

/* ---------- UI helper functions ---------- */
function addFieldOnly() {
  viewEntries.value.push({ id: idCounter++, field: "" });
}
function addFieldValue() {
  sortEntries.value.push({ id: idCounter++, field: "", value: "" });
}
function removeField(i, type) {
  (type === "view" ? viewEntries : sortEntries).value.splice(i, 1);
}
function getAvailableFields(arr, current) {
  const picked = arr.map((e) => e.field).filter((f) => f && f !== current);
  return allFields.filter((f) => !picked.includes(f));
}
const getAvailableFieldsForView = (c) =>
  getAvailableFields(viewEntries.value, c);
const getAvailableFieldsForSort = (c) =>
  getAvailableFields(sortEntries.value, c);
function handleFieldChange() {
  viewEntries.value = [...viewEntries.value]; // force reactivity
  sortEntries.value = [...sortEntries.value];
}

/* ---------- fetch datasets with current filters/sorts ---------- */
async function handleSubmit() {
  try {
    const r = await fetch("http://127.0.0.1:5000", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        type: "manage",
        viewEntries: viewEntries.value,
        sortEntries: sortEntries.value,
      }),
    });
    const j = await r.json();
    if (j.status === "success") {
      queryResults.value = j.data;
    } else {
      throw new Error(j.message || "Failed to fetch data");
    }
  } catch (e) {
    console.error("Fetch error:", e);
    alert("Error fetching data");
  }
}

/* ---------- editing logic ---------- */
function startEdit(i) {
  editIndex.value = i;
  editedRow.value = JSON.parse(JSON.stringify(queryResults.value[i]));

  // Pretty print JSON fields
  if (typeof editedRow.value.metadata === "object")
    editedRow.value.metadata = JSON.stringify(
      editedRow.value.metadata,
      null,
      2
    );
  if (typeof editedRow.value.pool === "object")
    editedRow.value.pool = JSON.stringify(editedRow.value.pool, null, 2);
}

function cancelEdit() {
  editIndex.value = -1;
  editedRow.value = {};
}

async function saveEdit(i) {
  try {
    if (!confirm("Are you sure you want to save changes to this dataset?")) {
      return;
    }

    if (editedRow.value.metadata)
      editedRow.value.metadata = JSON.parse(editedRow.value.metadata);
    if (editedRow.value.pool)
      editedRow.value.pool = JSON.parse(editedRow.value.pool);

    ["paused", "rgb", "category"].forEach((k) => {
      if (k in editedRow.value && typeof editedRow.value[k] === "string")
        editedRow.value[k] = editedRow.value[k].trim().toLowerCase() === "true";
    });

    if (typeof editedRow.value.tags === "string") {
      editedRow.value.tags = editedRow.value.tags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);
    }

    ["aux_data", "band_info", "remarks"].forEach((k) => {
      if (editedRow.value[k] === "") editedRow.value[k] = null;
    });

    const payload = JSON.parse(JSON.stringify(editedRow.value));

    const r = await fetch("http://127.0.0.1:5000", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: "edit", value_edit: payload }),
    });
    const j = await r.json();

    if (j.status === "success") {
      queryResults.value[i] = payload;
      cancelEdit();
      alert("Saved successfully!");
    } else {
      throw new Error(j.message);
    }
  } catch (e) {
    console.error("Save failed:", e);
    alert("Save failed – check JSON fields & booleans.");
  }
}

/* ---------- delete logic ---------- */
function deleteDataset(id) {
  if (!confirm("Are you sure you want to delete this dataset?")) {
    return; // User cancelled, no delete
  }
  fetch("http://127.0.0.1:5000/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type: "delete",
      id: id,
    }),
  })
    .then((res) => {
      if (!res.ok)
        throw new Error(`Server responded with status ${res.status}`);
      return res.json();
    })
    .then((data) => {
      if (data.status === "success") {
        alert("Deleted successfully!");
        handleSubmit(); // <==== RELOAD the table data here
      } else {
        alert("Error: " + data.message);
      }
    })
    .catch((err) => {
      console.error("Delete failed:", err);
    });
}

/* ---------- run initial fetch ---------- */
onMounted(handleSubmit);
</script>

<style scoped>
#manag {
  height: 75dvh;
  overflow-y: auto;
}
@media (max-width: 767px) {
  #manag {
    height: 62vh;
  }
}
</style>
