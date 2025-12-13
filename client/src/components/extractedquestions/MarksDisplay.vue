<script setup>
const props = defineProps({
  marks: {
    type: String,
    required: true
  }
});
</script>

<template>
  <div class="p-2 bg-gray-200 rounded-md inline-block">
    <p class="text-sm font-semibold">[{{ props.marks }} marks]</p>
  </div>
</template>
