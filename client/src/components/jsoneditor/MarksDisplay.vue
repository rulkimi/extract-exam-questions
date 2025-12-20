<script setup>
const props = defineProps({
  marks: {
    type: Number,
    required: true
  }
});
</script>

<template>
  <div class="p-2 rounded-md inline-block text-right">
    <p class="text-sm font-semibold">[{{ props.marks }} marks]</p>
  </div>
</template>
