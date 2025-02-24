<script setup>
import Sidebar from '@/components/Sidebar.vue';
</script>

<template>
  <div class="flex bg-teal-50">
    <Sidebar />
    <div class="p-4">
      <slot></slot>
    </div>
  </div>
</template>