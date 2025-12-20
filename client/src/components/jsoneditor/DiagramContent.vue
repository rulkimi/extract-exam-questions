<script setup>
import { computed, inject, ref, watch, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  content: {
    type: Object,
    required: true
  }
})

const imageData = inject('imageData', []);
const imageLoaded = ref(false)
const currentImageSrc = ref('')
const loadingImage = ref(false)

const imageUrl = computed(() => {
  const arr = Array.isArray(imageData.value) ? imageData.value : [];
  return arr.find(
    img =>
      String(img.page) === String(props.content.page) &&
      img.type === props.content.type &&
      String(img.number).replace(/\s+/g, '') === String(props.content.number).replace(/\s+/g, '')
  )?.url;
});

// Preload and manage image loading
const loadImage = (src) => {
  if (!src || currentImageSrc.value === src) return;
  
  loadingImage.value = true;
  imageLoaded.value = false;
  
  const img = new Image();
  img.onload = () => {
    currentImageSrc.value = src;
    imageLoaded.value = true;
    loadingImage.value = false;
  };
  img.onerror = () => {
    loadingImage.value = false;
  };
  img.src = src;
};

// Watch for URL changes and preload new images
watch(imageUrl, (newUrl) => {
  if (newUrl) {
    loadImage(newUrl);
  } else {
    currentImageSrc.value = '';
    imageLoaded.value = false;
  }
}, { immediate: true });

// Cleanup on unmount
onUnmounted(() => {
  currentImageSrc.value = '';
  imageLoaded.value = false;
});
</script>

<template>
  <div class="flex flex-col items-center justify-center">
    <!-- Show loading state while image is loading -->
    <div v-if="loadingImage" 
      class="block flex flex-col max-w-lg w-full h-[200px] border border-black bg-gray-100 text-center items-center justify-center">
      <span class="block text-xl font-bold opacity-40">Loading diagram...</span>
    </div>
    
    <!-- Show loaded image -->
    <img v-else-if="imageLoaded && currentImageSrc" 
      :src="currentImageSrc" 
      alt="Diagram Image" 
      class="mt-2 max-w-3/4 h-auto border border-black" />
    
    <!-- Show placeholder when no image available -->
    <div v-else
      class="block flex flex-col max-w-lg w-full h-[200px] border border-black bg-gray-300 text-center items-center justify-center">
      <span class="block text-xl font-bold opacity-20">-Diagram not extracted-</span>
      <span class="block text-xl font-bold opacity-20">Page {{ content.page }}</span>
    </div>
    
    <span class="block">Rajah {{ content.number }}</span>
    <span class="block"><em>Diagram</em> {{ content.number }}</span>
  </div>
</template>
