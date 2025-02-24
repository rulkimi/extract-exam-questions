<script setup>
import FileUploadBox from "@/components/FileUploadBox.vue";
</script>

<template>
  <FileUploadBox
    description="PDF files not more than 20MB"
    verticalUI
    accept=".pdf"
  />
</template>
