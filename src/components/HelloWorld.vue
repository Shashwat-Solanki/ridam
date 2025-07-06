<template>
  <div class="container-fluid p-3" id="displ">
    <!-- Buttons at top, horizontally aligned -->

    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <img src="../components/images/sac.png" alt="SAC" style="height: 8vh" />
      <h5 class="text-center flex-grow-1 m-0" id="titl">
        RIDaM Data Management System
      </h5>
      <img src="../components/images/isro.png" alt="ISRO" style="height: 8vh" />
    </div>
    <div class="d-flex justify-content-start mb-3 gap-2 flex-wrap">
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

    <!-- Main Layout -->
    <div class="row">
      <div class="col-12" id="scree">
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

#scree {
  height: 75dvh;
  overflow-y: hidden;
  border-radius: 10px;
}

#displ {
  background-color: #1f2839;
  height: 100dvh;
}

/* Title font size and text change on smaller screens */
#titl {
  color: #f5f5ef;
  font-size: 2dvw;
  font-weight: bolder;
  transition: font-size 0.3s ease;
}

/* Change title text and size on small screens */
@media (max-width: 767px) {
  #titl {
    font-size: 4vw;
  }
  #titl::after {
    content: "RIDaM DMS";
    display: block;
    text-align: center;
    color: #f5f5ef;
  }
  #titl {
    /* Hide original text on small screens */
    color: transparent;
    position: relative;
  }
}
</style>
