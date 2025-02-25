<script setup>
defineProps({
  marks: {
    type: Number,
    required: true
  }
})
</script>

<template>
  <span class="block">[{{ marks }} Markah]</span>
  <span class="block">[{{ marks }} <em>{{ marks > 1 ? 'Marks' : 'Mark' }}</em>]</span>
</template>