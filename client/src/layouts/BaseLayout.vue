<script setup>
import Sidebar from '@/components/Sidebar.vue';
import AlertToast from '@/components/AlertToast.vue';
</script>

<template>
  <div class="flex bg-indigo-50">
    <Sidebar />
    <div class="p-4 flex-grow max-h-screen overflow-hidden">
      <RouterView></RouterView>
    </div>
  </div>
  <AlertToast />
</template>