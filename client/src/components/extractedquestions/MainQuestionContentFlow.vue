<script setup>
import ContentFlow from './ContentFlow.vue';

const props = defineProps({
  content: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    required: true
  },
  number: {
    type: String,
    required: true
  }
});
</script>

<template>
  <tr class="border bg-blue-50">
    <td v-if="props.number && props.index === 0" class="border p-2 w-16">{{ props.number }}</td>
    <td v-else class="border p-2 w-16"></td>
    <td class="border p-2 space-y-6" colspan="3">
      <ContentFlow :content="props.content" />
    </td>
  </tr>
</template>
