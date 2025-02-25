<script setup>
import FileUploadBox from "@/components/FileUploadBox.vue";
import axios from 'axios';
import { ref } from 'vue';
import { useRouter } from "vue-router";

const loading = ref(false);
const router = useRouter();
const uploadSuccess = ref(false)
const pdf = ref()

const uploadFile = async (file) => {
  pdf.value = URL.createObjectURL(file)
  loading.value = true;
  try {
    const formData = new FormData();
    formData.append('pdf_file', file);
    const response = await axios.post(import.meta.env.VITE_BACKEND_URL + '/extract_questions', formData);
    const { status } = response.data;
    if (status === "success") {
      uploadSuccess.value = true;
    }
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
      v-if="!uploadSuccess"
      description="PDF files not more than 30MB"
      verticalUI
      accept=".pdf"
      :max-size="30"
      :loading="loading"
      @upload-files="uploadFile"
    />
    <div v-else class="flex flex-col items-center">
      <font-awesome-icon class="text-teal-500 mb-2 size-[5rem]" :icon="['fas', 'check-circle']" />
      <p class="text-lg text-gray-700">Upload successful! Your file is being processed.</p>
      <div class="flex gap-2 mt-4">
        <router-link
          to="/docs"
          class="px-4 py-2 text-teal-500 border border-teal-500 hover:bg-teal-500 hover:text-white rounded"
        >
          Back to Documents
        </router-link>
        <button
          class="px-4 py-2 bg-teal-500 text-white rounded hover:bg-teal-600"
          @click="uploadSuccess = false"
        >
          Upload another file
        </button>
      </div>
    </div>
  </div>
</template>
