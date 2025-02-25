<script setup>
import { useRoute } from 'vue-router';
import { ref, onMounted } from 'vue';
import PDFViewerWithNavigation from '@/components/PDFViewerWithNavigation.vue';
import JSONEditor from '@/components/JSONEditor.vue';
import axios from 'axios'

const route = useRoute();
const id = route.params.id;
const documentDetail = ref(null)

const fetchDocumentDetail = async () => {
  try {
    const response = await axios.get(import.meta.env.VITE_BACKEND_URL + `/documents/${id}`);
    const { data, status, message } = response.data;
    documentDetail.value = data;
    console.log(documentDetail.value)
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  fetchDocumentDetail()
});
</script>

<template>
  <div class="flex h-full w-full">
    <JSONEditor
      v-if="documentDetail && documentDetail.data"
      class="h-full overflow-auto w-2/3" :all-questions="documentDetail.data"
    />
    <PDFViewerWithNavigation
      v-if="documentDetail && documentDetail.file_url"
      :id="id"
      class="w-1/3"
      :scale="0.60"
      :file-name="documentDetail.file_name"
      :fileURL="documentDetail.file_url"
    />
  </div>
</template>

