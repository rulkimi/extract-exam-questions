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

    </div>
  </div>
</template>
