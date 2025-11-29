<script setup>
import { useRoute } from 'vue-router';
import { ref, onMounted } from 'vue';
import PDFViewerWithNavigation from '@/components/PDFViewerWithNavigation.vue';
import JSONEditor from '@/components/jsoneditor/index.vue';
import apiClient from '@/api';

const documentDetail = ref(null)

const props = defineProps({
  id: {
    type: String,
    required: true
  }
})

const fetchDocumentDetail = async () => {
  try {
    const response = await apiClient.get(`/documents/${props.id}`);
    const { data, status, message } = response.data;
    documentDetail.value = data;
    // console.log(documentDetail.value.image_data)
  } catch (error) {
    console.error(error)
  }
}

function download(jsonData, pdfname) {
  const filename = pdfname.replace(/\.pdf$/, '.docx');
  const imageData = documentDetail.value?.image_data;

  apiClient.post('/generate_word', { jsonData, imageData, filename }, {
    responseType: 'blob' // This is important for file downloads
  })
    .then(response => {
      const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename); // Use the specified filename
      document.body.appendChild(link);
      link.click();
      link.remove();
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

onMounted(() => {
  fetchDocumentDetail()
});
</script>

<template>
  <div class="space-y-2 mb-4 p-4">
    <div class="flex justify-between items-center text-black">
      <router-link to="/list" class="font-medium hover:bg-gray-200 px-3 py-2 rounded-lg">
        <font-awesome-icon :icon="['fas', 'arrow-left']" class="mr-2" />
        Back to Dashboard
      </router-link>
      <div class="flex items-center flex-col">
        <h1 class="text-xl font-semibold">Document Detail</h1>
        <span v-if="documentDetail" class="text-gray-500">{{ documentDetail.file_name }}</span>
      </div>

      <button @click="download(documentDetail.data, documentDetail.file_name)"
        class="px-3 py-2 bg-indigo-500 text-white rounded-lg font-semibold hover:bg-indigo-600">
        <font-awesome-icon class="mx-2" :icon="['fas', 'download']" />Download .docx</button>
    </div>

  </div>
  <div class="flex h-[92%]">
    <JSONEditor v-if="documentDetail && documentDetail.data" class="h-full overflow-auto w-1/2"
      :data="documentDetail.data" :image_data="documentDetail?.image_data" />
    <PDFViewerWithNavigation v-if="documentDetail && documentDetail.file_url" :id="id" class="w-1/2" :auto-fit="true"
      :file-name="documentDetail.file_name" :fileURL="documentDetail.file_url" />
  </div>
</template>
