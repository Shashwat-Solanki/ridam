<!-- RegisterForm.vue -->
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

    <!-- + Add Metadata -->
    <div class="row mb-3">
      <div class="offset-sm-2 col-sm-10">
        <button
          type="button"
          class="btn btn-outline-info w-100 w-sm-auto"
          @click="addMetadata"
          :disabled="form.metadata.length >= allKeyOptions.length">
          + Add Metadata
        </button>
      </div>
    </div>

    <!-- Dynamic Metadata Rows -->
    <div class="row mb-3" v-for="(meta, index) in form.metadata" :key="index">
      <!-- Key -->
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

      <!-- Value -->
      <label class="col-sm-2 col-form-label">Value</label>
      <div class="col-sm-3">
        <input
          type="text"
          class="form-control"
          v-model="meta.value"
          placeholder="Enter Value" />
      </div>

      <!-- Remove -->
      <div class="col-sm-1 d-flex align-items-center justify-content-end">
        <button
          class="btn btn-sm btn-danger"
          @click.prevent="removeMetadata(index)">
          ×
        </button>
      </div>
    </div>

    <!-- Dropdown fields -->
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

    <!-- Text fields -->
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
import { reactive, toRaw } from "vue";

/* ---------- form state ---------- */
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
  metadata: [], // <- edits happen here
});

/* ---------- static field data ---------- */
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

/* ---------- metadata helpers ---------- */
const allKeyOptions = [
  "Location",
  "City",
  "Contact_Person",
  "Organization",
  "Mailing_Address",
  "Country",
  "Contact_Telephone",
];

function availableKeyOptions(rowIndex) {
  // keys not used by other rows, plus the key in this row
  return allKeyOptions.filter(
    (opt) =>
      form.metadata.findIndex((m, i) => i !== rowIndex && m.key === opt) === -1
  );
}

function addMetadata() {
  const nextKey = allKeyOptions.find(
    (k) => !form.metadata.some((m) => m.key === k)
  );
  if (nextKey) form.metadata.push({ key: nextKey, value: "" });
}

function removeMetadata(i) {
  form.metadata.splice(i, 1);
}

/* ---------- submit handler ---------- */
async function onSubmit() {
  // turn [{key,value}, …]  ➜  { key: value, … }
  const metadataObj = Object.fromEntries(
    form.metadata.map(({ key, value }) => [key, value])
  );

  try {
    await fetch("http://127.0.0.1:5000", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        type: "register",
        ...toRaw(form),
        metadata: metadataObj, // <-- send the object, not the array
      }),
    });
    alert("Data Registered");
  } catch (err) {
    console.error(err);
    alert("Error occurred during data registration");
  }
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
