<script setup>
defineProps({
  content: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <span v-if="content.format === 'checkbox'">
    <div class="checkbox"></div>
  </span>
  <div v-else-if="content.format === 'multiple-choice'" class="space-y-4">
    <span v-for="(option, index) in content.options" :key="index" class="flex gap-8 items-center">
      <div class="w-16 h-12 border-2 border-black"></div>
      <div>
        {{ option.malay }} <br />
        <em>{{ option.english }}</em> <br />
      </div>
    </span>
  </div>
  <span v-else>
    ...........................................................................................................
  </span>
</template>

<style scoped>
.checkbox {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 1px solid black;
}
</style>