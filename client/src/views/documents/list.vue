<script setup>
import Table from '@/components/Table.vue';

const headers = [
  // { key: 'id', label: 'ID'  },
  { key: 'name', label: 'Name' },
  { key: 'status', label: 'Status' },
  { key: 'date', label: 'Date' },
  { key: 'actions', width: '100px' }
];

const data = [
  { id: 1, name: 'Kedah Physics P2 Q 2023.pdf', date: '2023-01-01', status: 'in process' },
  { id: 2, name: 'Trial Fizik P2 Kelantan 2022.pdf', date: '2023-01-02', status: 'extracted' },
  { id: 3, name: 'Physics P2 MRSM 2023.pdf', date: '2023-01-03', status: 'edited' },
];

const getStatusClass = (status) => {
  switch (status) {
    case 'in process':
      return 'border-indigo-500 text-indigo-500'; 
    case 'extracted':
      return 'border-teal-500 text-teal-500'; 
    case 'edited':
      return 'border-blue-500 text-blue-500'; 
    default:
      return 'border-gray-400'; 
  }
};

const deleteItem = (id) => {
  console.log(`Delete item with ID: ${id}`);
};

const onRowClick = (item) => {
  console.log(`Row clicked for the item with ID: ${item.id}. The data:`);
  console.table(item)
}
</script>

<template>
  <div class="flex items-center justify-between mb-4">
    <h1 class="text-xl font-semibold">List of Documents</h1>
    <router-link
      class="px-3 py-2 bg-teal-500 text-white rounded-lg font-semibold"
      to="/docs/upload"
    >
      Upload Paper
    </router-link>
  </div>
  <div class="bg-white rounded-lg p-4 border border-slate-200 shadow-sm">
    <Table clickable-row :headers="headers" :data="data" @row-click="onRowClick">
      <template #cell-content="{ rowData, header }">
        <div
          v-if="header.key === 'status'"
          class="px-2 py-1 w-fit rounded-full font-semibold text-xs border"
          :class="getStatusClass(rowData.status)"
        >
          {{ rowData.status.toUpperCase() }}
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