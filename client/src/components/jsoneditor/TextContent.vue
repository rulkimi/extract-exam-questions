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
    <div v-if="props.content.text.malay" v-html="props.content.text.malay"></div>
    <div v-if="props.content.text.english" class="mt-2 italic text-gray-600" v-html="props.content.text.english"></div>
  </div>
</template>
