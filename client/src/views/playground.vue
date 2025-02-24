<script setup>
import PDFViewerWithNavigation from '@/components/PDFViewerWithNavigation.vue';
</script>
<template>
  <div class="flex justify-between h-full">
    <PDFViewerWithNavigation id="pdf-viewer-1" file-name="File 1" fileURL="/sample-pdf.pdf" />
    <PDFViewerWithNavigation id="pdf-viewer-2" file-name="File 2" fileURL="/sample-pdf.pdf" />
  </div>
</template>