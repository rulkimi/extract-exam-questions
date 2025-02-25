<script setup>
defineProps({
  content: {
    type: Object,
    required: true
  },
})
</script>

<template>
  <div>{{ content.text.malay }}</div>
  <div class="italic">{{ content.text.english }}</div>
</template>