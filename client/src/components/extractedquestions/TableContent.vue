<script setup>
import RowContent from './RowContent.vue';

const props = defineProps({
  content: {
    type: Object,
    required: true
  }
});
</script>

<template>
  <div class="overflow-x-auto">
    <table class="w-full border-collapse border bg-white">
      <tbody>
        <RowContent v-for="(row, index) in props.content.rows" :key="index" :row="row" />
      </tbody>
    </table>
  </div>
</template>
