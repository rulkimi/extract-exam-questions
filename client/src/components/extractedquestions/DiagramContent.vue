<script setup>
import { inject } from 'vue';

const props = defineProps({
  content: {
    type: Object,
    required: true
  }
});

const imageData = inject('imageData');

const getImageUrl = (imageName) => {
  const image = imageData.find(img => img.name === imageName);
  return image ? image.path : '';
};
</script>

<template>
  <div class="p-4 bg-gray-100 rounded-md">
    <img :src="getImageUrl(props.content.image_name)" :alt="props.content.image_name" class="max-w-full h-auto" />
  </div>
</template>
