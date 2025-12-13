<script setup>
const props = defineProps({
  content: {
    type: Object,
    required: true
  }
});
</script>

<template>
  <div class="p-4 bg-gray-100 rounded-md">
    <p class="text-sm text-gray-600">Answer Space: {{ props.content.lines }} lines</p>
  </div>
</template>
