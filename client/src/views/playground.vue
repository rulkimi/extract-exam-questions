<script setup>
import PDFViewerWithNavigation from '@/components/PDFViewerWithNavigation.vue';
import JSONEditor from "@/components/JSONEditor.vue";
</script>
<template>
  <div class="flex justify-between h-full w-full">
    <JSONEditor class="h-full overflow-auto w-1/2" />
    <PDFViewerWithNavigation class="w-1/2" id="pdf-viewer-1" file-name="File 1" fileURL="/sample-pdf.pdf" />
    <!-- <PDFViewerWithNavigation id="pdf-viewer-2" file-name="File 2" fileURL="/sample-pdf.pdf" /> -->
  </div>
</template>