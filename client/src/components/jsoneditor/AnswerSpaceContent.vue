<script setup>
const props = defineProps({
  content: {
    type: Object,
    required: true
  }
});
</script>

<template>
  <div class="px-4 py-2 bg-gray-100 rounded-md">
    <!-- <p class="text-sm text-gray-600">Answer Space: {{ props.content.lines }} lines</p> -->
    <div v-if="props.content.format == 'line'">
      <div v-for="index in props.content.lines">
        <div class="mt-6 w-full border-b-2 border-black border-dotted"></div>
      </div>
    </div>
    <div v-else-if="props.content.format == 'blank-space'">
      <div class="w-full p-8 text-gray-600 text-center">[Blank Space]</div>
    </div>
  </div>
</template>
