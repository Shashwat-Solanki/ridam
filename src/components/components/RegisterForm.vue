<template>
  <form
    @submit.prevent="onSubmit"
    class="bg-light p-4 rounded shadow-sm"
    style="background-color: #1f2839"
    id="form_1">
    <!-- Name -->
    <div class="row mb-3">
      <label class="col-sm-2 col-form-label">Name</label>
      <div class="col-sm-10">
        <input
          v-model="form.name"
          type="text"
          class="form-control"
          placeholder="Enter Name" />
      </div>
    </div>

    <!-- Add Metadata Button -->
    <div class="row mb-3">
      <div class="offset-sm-2 col-sm-10">
        <button
          type="button"
          class="btn btn-outline-info w-100 w-sm-auto"
          @click="addMetadata"
          :disabled="metadata.length >= allKeyOptions.length">
          + Add Metadata
        </button>
      </div>
    </div>

    <!-- Dynamic Metadata Rows -->
    <div class="row mb-3" v-for="(meta, index) in metadata" :key="index">
      <!-- Key dropdown -->
      <label class="col-sm-2 col-form-label">Key</label>
      <div class="col-sm-4 mb-2 mb-sm-0">
        <select class="form-select" v-model="meta.key">
          <option
            v-for="opt in availableKeyOptions(index)"
            :key="opt"
            :value="opt">
            {{ opt }}
          </option>
        </select>
      </div>

      <!-- Value textbox -->
      <label class="col-sm-2 col-form-label">Value</label>
      <div class="col-sm-3">
        <input
          type="text"
          class="form-control"
          v-model="meta.value"
          placeholder="Enter Value" />
      </div>

      <!-- Remove row -->
      <div class="col-sm-1 d-flex align-items-center justify-content-end">
        <button
          class="btn btn-sm btn-danger"
          @click.prevent="removeMetadata(index)">
          ×
        </button>
      </div>
    </div>

    <!-- Dropdown Fields -->
    <div class="row mb-3" v-for="field in dropdownFields" :key="field.label">
      <label class="col-sm-2 col-form-label">{{ field.label }}</label>
      <div class="col-sm-10">
        <select
          class="form-select"
          v-model="form[field.label.replaceAll(' ', '')]">
          <option v-for="opt in field.options" :key="opt" :value="opt">
            {{ opt }}
          </option>
        </select>
      </div>
    </div>

    <!-- Text Fields -->
    <div class="row mb-3" v-for="field in textFields" :key="field">
      <label class="col-sm-2 col-form-label">{{ field }}</label>
      <div class="col-sm-10">
        <input
          v-model="form[field.replaceAll(' ', '').replaceAll('-', '')]"
          type="text"
          class="form-control" />
      </div>
    </div>

    <div class="text-end">
      <button type="submit" class="btn btn-danger">Register</button>
    </div>
  </form>
</template>

<script setup>
import { ref } from "vue";
import { reactive } from "vue";

const form = reactive({
  name: "",
  Frequency: "",
  Extension: "",
  Projections: "",
  Paused: "",
  RGB: "",
  Category: "",
  BandInfo: "",
  AuxData: "",
  Remarks: "",
  Tags: "",
  ThemeID: "",
  SubThemeID: "",
  metadata: [],
});

async function onSubmit() {
  try {
    await fetch("http://127.0.0.1:5000", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(form),
    });
    alert("Data Registerd");
  } catch (err) {
    console.log(err);
    alert("Error Occured during data registration");
  }
}

/* --- static data --- */
const dropdownFields = [
  { label: "Frequency", options: ["Daily", "Weekly", "Monthly"] },
  { label: "Extension", options: [".tif"] },
  { label: "Projections", options: ["EPSG:4326", "EPSG:3857"] },
  { label: "Paused", options: ["False", "True"] },
  { label: "RGB", options: ["False", "True"] },
  { label: "Category", options: ["False", "True"] },
];

const textFields = [
  "Band Info",
  "Aux Data",
  "Remarks",
  "Tags",
  "Theme ID",
  "Sub -Theme ID",
];

/* --- metadata logic --- */
const allKeyOptions = [
  "Location",
  "City",
  "Contact_Person",
  "Organization",
  "Mailing_Address",
  "Country",
  "Contact_Telephone",
];

const metadata = ref([]);

/**
 * Return only keys that are not yet picked in other rows.
 * Always include the key already chosen in this row (so the
 * dropdown doesn’t suddenly hide its current value).
 */
function availableKeyOptions(rowIndex) {
  return allKeyOptions.filter(
    (opt) =>
      metadata.value.findIndex((m, i) => i !== rowIndex && m.key === opt) === -1
  );
}

/* add a new row pre-filled with the first unused key */
function addMetadata() {
  const nextKey = allKeyOptions.find(
    (k) => !metadata.value.some((m) => m.key === k)
  );
  if (nextKey) metadata.value.push({ key: nextKey, value: "" });
}

/* remove row */
function removeMetadata(i) {
  metadata.value.splice(i, 1);
}
</script>

<style scoped>
#form_1 {
  height: 82vh;
  overflow-y: auto;
}
@media (max-width: 767px) {
  #form_1 {
    height: 62vh;
  }
}
</style>
