<script setup>
import AnswerSpaceContent from './AnswerSpaceContent.vue';
import DiagramContent from './DiagramContent.vue';
import TextContent from './TextContent.vue';

const props = defineProps({
  content: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <div v-if="content.type === 'text'">
    <TextContent :content="content" />
  </div>
  <div v-if="content.type === 'diagram'">
    <DiagramContent />
  </div>
  <div v-if="content.type === 'answer_space'">
    <AnswerSpaceContent :content="content" />
  </div>
</template>