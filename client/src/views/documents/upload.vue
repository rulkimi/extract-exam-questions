<script setup>
import FileUploadBox from "@/components/FileUploadBox.vue";
</script>

<template>
  <div class="space-y-2 mb-4">
    <h1 class="text-xl font-semibold">Upload Paper</h1>
    <nav>
      <ol class="list-reset flex items-center">
        <li>
          <router-link to="/docs" class="text-teal-500 hover:underline">Documents</router-link>
        </li>
        <font-awesome-icon class="mx-2" :icon="['fas', 'chevron-right']" size="xs" />
        <li class="text-gray-500">Upload Paper</li>
      </ol>
    </nav>
  </div>
  <div class="flex w-full justify-center">
    <FileUploadBox
      description="PDF files not more than 20MB"
      verticalUI
      accept=".pdf"
      :loading="false"
    />
  </div>
</template>
