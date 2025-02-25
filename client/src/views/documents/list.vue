<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios"
import Table from '@/components/Table.vue';
import { formatDate } from "@/utils";

const headers = [
  // { key: 'id', label: 'ID'  },
  { key: 'file_name', label: 'Name' },
  { key: 'status', label: 'Status' },
  { key: 'uploaded_date', label: 'Date' },
  { key: 'actions', width: '100px' }
];
const tableData = ref([])
const loading = ref(false)
onMounted(() => {
  fetchDocuments()
})
const fetchDocuments = async () => {
  loading.value = true;
  try {
    const response = await axios.get(import.meta.env.VITE_BACKEND_URL + '/documents');
    const { data, message, status } = response.data;
    tableData.value = data.documents;
    console.log(tableData.value)
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false;
  }
}

const getStatusClass = (status) => {
  switch (status) {
    case 'in process':
      return 'border-indigo-500 text-indigo-500'; 
    case 'extracted':
      return 'border-teal-500 text-teal-500'; 
    case 'edited':
      return 'border-blue-500 text-blue-500'; 
    case 'failed':
      return 'border-red-500 text-red-500'; 
    default:
      return 'border-gray-400'; 
  }
};

const deleteItem = (id) => {
  console.log(`Delete item with ID: ${id}`);
};

const router = useRouter()
const onRowClick = (item) => {
  if (item.status === 'failed' || item.status === 'in process') {
    alert(`Item is ${item.status}. Please try again later or contact the team.`);
    return;
  }
  router.push({ name: 'doc-detail', params: { id: item.id } });
}

</script>

<template>
  <div class="flex justify-between mb-4">
    <h1 class="text-xl font-semibold">Documents</h1>
    <router-link
      class="px-3 py-2 bg-teal-500 text-white rounded-lg font-semibold"
      to="/docs/upload"
    >
      Upload Paper
    </router-link>
  </div>
  <div class="bg-white rounded-lg p-4 border border-slate-300 shadow-sm">
    <Table
      clickable-row
      :headers="headers"
      :data="tableData"
      @row-click="onRowClick"
      no-result-statement="No document found. Upload one to start"
      :loading="loading"
    >
      <template #cell-content="{ rowData, header }">
        <div
          v-if="header.key === 'status'"
          class="px-2 py-1 w-fit rounded-full font-semibold text-xs border"
          :class="getStatusClass(rowData.status)"
        >
          {{ rowData.status.toUpperCase() }}
        </div>
        <div
          v-else-if="header.key === 'uploaded_date'"
        >
          {{ formatDate(rowData[header.key]) }}
        </div>
        <div v-else-if="header.key === 'actions'">
          <div class="flex justify-end space-x-2">
            <button
              v-if="rowData.status === 'extracted' || rowData.status === 'edited'"
              class="px-2 py-1 rounded-lg border border-teal-500 text-teal-500 hover:text-white hover:bg-teal-500"
            >
              Download
            </button>
            <button
              class="text-red-500 hover:text-white px-2 py-1 border border-red-500 hover:bg-red-500 rounded-lg"
              @click="deleteItem(rowData.id)"
            >
              <font-awesome-icon :icon="['fas', 'trash-can']" />
            </button>
          </div>
        </div>
        <div v-else>
          {{ rowData[header.key] }}
        </div>
      </template>
    </Table>
  </div>
</template>