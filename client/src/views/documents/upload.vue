<script setup>
import FileUploadBox from "@/components/FileUploadBox.vue";
import axios from 'axios';
import { ref } from 'vue';

const loading = ref(false);

const uploadFile = async (file) => {
  loading.value = true;
  try {
    const formData = new FormData();
    formData.append('pdf_file', file);
    const response = await axios.post(import.meta.env.VITE_BACKEND_URL + '/extract_questions', formData);
    console.log(response.data);
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false;
  }
}
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
      description="PDF files not more than 30MB"
      verticalUI
      accept=".pdf"
      :max-size="30"
      :loading="loading"
      @upload-files="uploadFile"
    />
  </div>
</template>
