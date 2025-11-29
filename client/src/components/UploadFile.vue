<script setup>
import FileUploadBox from "@/components/FileUploadBox.vue";
import apiClient from '@/api';
import { ref, computed } from 'vue';

const API_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_BACKEND_URL;
const loading = ref(false);
const uploadSuccess = ref(false)
const pdf = ref()

const subject = ref('Physics');
const subjects = [
  'Physics',
  'Chemistry (Experimental)',
  'Biology (Experimental)',
];

const questionPaper = ref(null);
const answerScheme = ref(null);

const emit = defineEmits(['uploaded', 'cancel'])

const uploadFile = async (file) => {
  pdf.value = URL.createObjectURL(file)
  loading.value = true;
  try {
    const formData = new FormData();
    formData.append('pdf_file', file);
    formData.append('subject', subject.value);
    const response = await apiClient.post('/extract_questions', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    const { status } = response.data;
    if (status === "success") {
      uploadSuccess.value = true;
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false;
    emit('uploaded')
  }
}

const canStart = computed(() => !!questionPaper.value && !!subject.value && !loading.value);

const onQuestionChange = (file) => { questionPaper.value = Array.isArray(file) ? file[0] : file || null; };
const onAnswerChange = (file) => { answerScheme.value = Array.isArray(file) ? file[0] : file || null; };

const startProcessing = () => {
  if (!questionPaper.value) return;
  uploadFile(questionPaper.value);
};

const cancel = () => {
  questionPaper.value = null;
  answerScheme.value = null;
  subject.value = 'Physics';
  uploadSuccess.value = false;
  emit('cancel');
};
</script>

<template>
  <div class="flex w-full justify-center">
    <div v-if="!uploadSuccess" class="w-[520px]">
      <p class="text-gray-500 mb-4">
        Upload your question paper and optionally an answer scheme. AI will extract and digitize the content.
      </p>

      <div class="text-sm font-medium text-gray-800 mb-2">
        Question Paper <span class="text-red-500">*</span>
      </div>
      <FileUploadBox
        :title-text="'Drag and drop your PDF here, or click to browse'"
        description="PDF files only"
        accept=".pdf"
        :max-size="30"
        :loading="loading"
        verticalUI
        mediumIcon
        :no-upload-button="true"
        :no-cancel-button="true"
        :dropzone-width="'520px'"
        :hide-browse-button="true"
        @file-changes="onQuestionChange"
      />

      <div class="text-sm font-medium text-gray-800 mt-5 mb-2">
        Answer Scheme <span class="text-gray-400">(Coming soon)</span>
      </div>
      <FileUploadBox
        :title-text="'Coming soon'"
        description="This feature is coming soon."
        accept=".pdf"
        :max-size="30"
        :loading="true"
        verticalUI
        mediumIcon
        :no-upload-button="true"
        :no-cancel-button="true"
        :dropzone-width="'520px'"
        :hide-browse-button="true"
      />

      <div class="mt-5">
        <label class="block text-sm font-medium text-gray-800 mb-2">
          Subject <span class="text-red-500">*</span>
        </label>
        <select
          v-model="subject"
          class="w-full bg-gray-100 border border-gray-200 rounded-md p-3 text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option v-for="s in subjects" :key="s" :value="s">{{ s }}</option>
        </select>
        <p class="text-sm text-gray-400 mt-2">
          Select the subject to help categorize your document
        </p>
      </div>

      <div class="flex justify-end gap-3 mt-6">
        <button type="button" class="px-4 py-2 rounded-lg border text-gray-700 hover:bg-gray-50" @click="cancel">
          Cancel
        </button>
        <button
          type="button"
          class="px-4 py-2 rounded-lg bg-indigo-500 text-white disabled:opacity-50"
          :disabled="!canStart"
          @click="startProcessing"
        >
          Start Processing
        </button>
      </div>
    </div>

    <div v-else class="flex flex-col items-center">
      <font-awesome-icon class="text-indigo-500 mb-2 size-[5rem]" :icon="['fas', 'check-circle']" />
      <p class="text-lg text-gray-700">Upload successful! Your file is being processed.</p>

    </div>
  </div>
</template>
