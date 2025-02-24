<script setup>
import FileUploadBox from "@/components/FileUploadBox.vue";
import axios from 'axios';
import { ref } from 'vue';
import { useRouter } from "vue-router";
import PDFViewerWithNavigation from "@/components/PDFViewerWithNavigation.vue";

const loading = ref(false);
const router = useRouter();
const pdf = ref()

const uploadFile = async (file) => {
  pdf.value = URL.createObjectURL(file)
  loading.value = true;
  try {
    const formData = new FormData();
    formData.append('pdf_file', file);
    const response = await axios.post(import.meta.env.VITE_BACKEND_URL + '/extract_questions', formData);
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
  <div v-if="pdf" class="flex w-full justify-center">
    <PDFViewerWithNavigation
      id="pdf-viewer"
      file-name="Uploaded Document"
      :fileURL="pdf"
      :scale="1.0"
      @total-pages="totalPages => console.log(totalPages)"
    />
  </div>
</template>
