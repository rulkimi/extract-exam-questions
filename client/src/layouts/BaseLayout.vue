<script setup>
import Sidebar from '@/components/Sidebar.vue';
import AlertToast from '@/components/AlertToast.vue';
</script>

<template>
  <div class="flex bg-teal-50">
    <Sidebar />
    <div class="p-4 flex-grow max-h-screen overflow-hidden">
      <slot></slot>
    </div>
  </div>
  <AlertToast />
</template>