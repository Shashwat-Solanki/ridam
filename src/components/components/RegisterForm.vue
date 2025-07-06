<template>
  <div class="d-flex justify-content-center">
    <div class="col-12 col-md-10 col-lg-8">
      <!-- STEP 1 – dataset info -->
      <form
        v-if="step === 1"
        @submit.prevent="step++"
        class="bg-light p-4 rounded shadow-sm"
        id="form_1">
        <!-- Name -->
        <div class="row mb-3">
          <label class="col-sm-2 col-form-label text-dark required">Name</label>
          <div class="col-sm-8">
            <input
              v-model="form.name"
              type="text"
              class="form-control form-control-sm"
              required
              placeholder="Enter Name" />
          </div>
        </div>

        <!-- + Add Metadata -->
        <div class="row mb-3">
          <div class="offset-sm-2 col-sm-8">
            <button
              type="button"
              class="btn btn-outline-info btn-sm w-100 w-sm-auto"
              @click="addMetadata"
              :disabled="form.metadata.length >= allKeyOptions.length">
              + Add Metadata
            </button>
          </div>
        </div>

        <!-- Metadata rows -->
        <div class="row mb-3" v-for="(m, i) in form.metadata" :key="i">
          <label class="col-sm-2 col-form-label text-dark required">Key</label>
          <div class="col-sm-3">
            <select class="form-select form-select-sm" v-model="m.key" required>
              <option v-for="opt in availableKeyOptions(i)" :key="opt">
                {{ opt }}
              </option>
            </select>
          </div>
          <label class="col-sm-2 col-form-label text-dark required"
            >Value</label
          >
          <div class="col-sm-3">
            <input
              class="form-control form-control-sm"
              v-model="m.value"
              required />
          </div>
          <div class="col-sm-2 d-flex align-items-center justify-content-end">
            <button
              class="btn btn-sm btn-danger"
              @click.prevent="removeMetadata(i)">
              ×
            </button>
          </div>
        </div>

        <!-- dropdown & text fields -->
        <div class="row mb-3" v-for="f in dropdownFields" :key="f.label">
          <label class="col-sm-2 col-form-label text-dark required">{{
            f.label
          }}</label>
          <div class="col-sm-8">
            <select
              class="form-select form-select-sm"
              v-model="form[f.label.replaceAll(' ', '')]"
              required>
              <option v-for="opt in f.options" :key="opt">{{ opt }}</option>
            </select>
          </div>
        </div>
        <div class="row mb-3" v-for="f in textFields" :key="f">
          <label
            class="col-sm-2 col-form-label text-dark"
            :class="{ required: !['Remarks', 'Aux Data'].includes(f) }">
            {{ f }}
          </label>
          <div class="col-sm-8">
            <input
              class="form-control form-control-sm"
              v-model="form[f.replaceAll(' ', '').replaceAll('-', '')]"
              :required="!['Remarks', 'Aux Data'].includes(f)" />
          </div>
        </div>
        <div class="text-end">
          <button class="btn btn-info btn-sm">Next ›</button>
        </div>
      </form>

      <!-- STEP 2 – product config -->
      <form
        v-else-if="step === 2"
        @submit.prevent="step++"
        class="bg-light p-4 rounded shadow-sm">
        <h5 class="mb-3 text-dark">Product configuration</h5>

        <label class="form-label text-dark">Product ID</label>
        <input
          class="form-control form-control-sm mb-3"
          :value="form.productId || ''"
          readonly />

        <label class="form-label text-dark required">Base path</label>
        <input
          class="form-control form-control-sm mb-3"
          v-model="form.basePath"
          required
          placeholder="/mnt/ridamairquality/..." />

        <div class="form-check mb-3">
          <input
            class="form-check-input"
            type="checkbox"
            v-model="form.createDir"
            id="dirchk" />
          <label class="form-check-label text-dark" for="dirchk">
            Create directory
          </label>
        </div>

        <div class="text-end">
          <button
            type="button"
            class="btn btn-secondary btn-sm me-2"
            @click="step--">
            ‹ Back
          </button>
          <button class="btn btn-info btn-sm">Next ›</button>
        </div>
      </form>

      <!-- STEP 3 – pyramid config -->
      <form
        v-else
        @submit.prevent="onSubmit"
        class="bg-light p-4 rounded shadow-sm">
        <h5 class="mb-3 text-dark">Pyramid configuration</h5>

        <label class="form-label text-dark">Pyramid ID</label>
        <input
          class="form-control form-control-sm mb-3"
          :value="form.pyramidId || ''"
          readonly />

        <div class="row">
          <div class="col">
            <label class="form-label text-dark required">From time</label>
            <input
              type="datetime-local"
              class="form-control form-control-sm"
              v-model="form.fromTime"
              required />
          </div>
          <div class="col">
            <label class="form-label text-dark required">To time</label>
            <input
              type="datetime-local"
              class="form-control form-control-sm"
              v-model="form.toTime"
              required />
          </div>
        </div>

        <label class="form-label text-dark mt-3 required"
          >Pools (JSON array)</label
        >
        <textarea
          class="form-control form-control-sm mb-4"
          rows="3"
          v-model="form.pool"
          required
          placeholder='["Pool 1","Pool 2"]'></textarea>

        <div class="text-end">
          <button
            type="button"
            class="btn btn-secondary btn-sm me-2"
            @click="step--">
            ‹ Back
          </button>
          <button class="btn btn-danger btn-sm">Register</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from "vue";

/* ── wizard step ── */
const step = ref(1);

/* ── reactive form ── */
const form = reactive({
  /* original fields */
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

  /* new fields (auto-filled) */
  productId: "",
  basePath: "",
  createDir: true,
  pyramidId: "",
  fromTime: "",
  toTime: "",
  pool: "",
});

/* ── static dropdown / text lists ── */
const dropdownFields = [
  { label: "Frequency", options: ["Daily", "Weekly", "Monthly"] },
  { label: "Extension", options: ["tif"] },
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

/* ── metadata helpers ── */
const allKeyOptions = [
  "Location",
  "City",
  "Contact_Person",
  "Organization",
  "Mailing_Address",
  "Country",
  "Contact_Telephone",
];
function availableKeyOptions(i) {
  return allKeyOptions.filter(
    (o) => form.metadata.findIndex((m, idx) => idx !== i && m.key === o) === -1
  );
}
function addMetadata() {
  const next = allKeyOptions.find(
    (k) => !form.metadata.some((m) => m.key === k)
  );
  if (next) form.metadata.push({ key: next, value: "" });
}
function removeMetadata(i) {
  form.metadata.splice(i, 1);
}

/* ── pool list ── */

/* ── sequential ID fetchers ── */
watch(
  () => [form.ThemeID, form.SubThemeID],
  async ([t, s]) => {
    if (!t || !s) return;
    const r = await fetch(`http://127.0.0.1:5000/next_product_id/${t}/${s}`);
    form.productId = (await r.json()).next;
    form.createDir = true;
  }
);

watch(
  () => form.productId,
  async (pid) => {
    if (!pid) return;
    const r = await fetch(`http://127.0.0.1:5000/next_pyramid_id/${pid}`);
    form.pyramidId = (await r.json()).next;
  }
);

/* ── submit ── */

async function onSubmit() {
  let poolJson = null;
  try {
    poolJson = JSON.parse(form.pool);
  } catch {
    alert("Pools field must be a valid JSON array!");
    return;
  }

  const metaObj = Object.fromEntries(
    form.metadata.map(({ key, value }) => [key, value])
  );

  const payload = {
    type: "register",
    ...form,
    metadata: metaObj,
    pool: poolJson, // send as actual JSON, not string
  };

  console.log("Payload:", payload);

  const res = await fetch("http://127.0.0.1:5000", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errMsg = await res.text();
    console.error("Backend error:", errMsg);
    alert("Failed to register: " + errMsg);
    return;
  }

  alert("Data registered ✔️");
  step.value = 1;
}
</script>

<style scoped>
.required::after {
  content: " *";
  color: #dc3545;
}
#form_1 {
  height: 75dvh;
  overflow-y: auto;
}
@media (max-width: 767px) {
  #form_1 {
    height: 62vh;
  }
}
</style>
