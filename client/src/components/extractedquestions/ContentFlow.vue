<script setup>
import TextContent from './TextContent.vue';
import DiagramContent from './DiagramContent.vue';
import TableContent from './TableContent.vue';
import AnswerSpaceContent from './AnswerSpaceContent.vue';

const props = defineProps({
  content: {
    type: Object,
    required: true
  }
});
</script>

<template>
  <div v-if="props.content.type === 'text'">
    <TextContent :content="props.content" />
  </div>
  <div v-else-if="props.content.type === 'diagram'">
    <DiagramContent :content="props.content" />
  </div>
  <div v-else-if="props.content.type === 'table'">
    <TableContent :content="props.content" />
  </div>
  <div v-else-if="props.content.type === 'answer_space'">
    <AnswerSpaceContent :content="props.content" />
  </div>
</template>
