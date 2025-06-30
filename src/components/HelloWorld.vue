<template>
  <div class="container-fluid p-3" id="displ">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <img src="../components/images/sac.png" alt="SAC" style="height: 8vh" />
      <h5 class="text-center flex-grow-1 m-0" id="titl">
        RIDaM Data Management System
      </h5>
      <img src="../components/images/isro.png" alt="ISRO" style="height: 8vh" />
    </div>

    <!-- Main Layout -->
    <div class="row">
      <!-- Sidebar -->
      <div class="col-md-2 mb-3">
        <div class="btn-group-vertical w-100">
          <button
            class="btn"
            :class="activeTab === 'Dashboard' ? 'btn-dark' : 'btn-light'"
            @click="activeTab = 'Dashboard'">
            Dashboard
          </button>
          <button
            class="btn"
            :class="activeTab === 'Register' ? 'btn-dark' : 'btn-light'"
            @click="activeTab = 'Register'">
            Register
          </button>
          <button
            class="btn"
            :class="activeTab === 'Management' ? 'btn-dark' : 'btn-light'"
            @click="activeTab = 'Management'">
            Management
          </button>
        </div>
      </div>

      <!-- Content Area -->
      <div class="col-md-10">
        <DashboardPanel v-if="activeTab === 'Dashboard'" />
        <RegisterForm v-if="activeTab === 'Register'" />
        <ManagementPanel v-if="activeTab === 'Management'" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import RegisterForm from "./components/RegisterForm.vue";
import ManagementPanel from "./components/ManagementPanel.vue";
import DashboardPanel from "./components/DashboardPanel.vue";

const activeTab = ref("Dashboard");
</script>

<style>
body {
  background-color: #1f2839;
}

#displ {
  background-color: #1f2839;
  height: 100dvh;
}

#titl {
  color: #f5f5ef;
  font-size: 2dvw;
  font-weight: bolder;
}
</style>
