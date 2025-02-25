<script setup>
import DiagramContent from './DiagramContent.vue';
import TextContent from './TextContent.vue';

defineProps({
  number: {
    type: String,
    required: true
  },
  content: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    required: true
  }
})
</script>

<template>
  <tr v-if="content.type === 'text'">
    <td v-if="index === 0">{{ number }}.</td>
    <td v-else></td>
    <td colspan="3">
      <TextContent :content="content" />
    </td>
  </tr>
  <tr v-if="content.type === 'diagram'">
    <td></td>
    <td colspan="3" style="text-align: center">
      <DiagramContent />
    </td>
  </tr>
  <tr v-if="content.type === 'answer_space'">
    <td colspan="3" class="answer-space">
      <span v-if="content.format === 'checkbox'">
        <div class="checkbox"></div>
      </span>
      <span v-else>
        ...........................................................................................................
      </span>
    </td>
  </tr>
</template>

<style scoped>
th,
td {
  border: 1px solid black;
  padding: 8px;
  vertical-align: top;
}
.checkbox {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 1px solid black;
}
</style>