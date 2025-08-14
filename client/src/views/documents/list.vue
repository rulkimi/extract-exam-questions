<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios"
import Table from '@/components/Table.vue';
import { formatDate } from "@/utils";
import { useToastStore } from "@/stores/toastStore";
import Dialog from "@/components/Dialog.vue";
import UploadFile from "@/components/UploadFile.vue";

const headers = [
	// { key: 'id', label: 'ID'  },
	{ key: 'file_name', label: 'Name' },
	{ key: 'status', label: 'Status' },
	{ key: 'uploaded_date', label: 'Date' },
	{ key: 'actions', width: '100px' }
];
const tableData = ref([])
const loading = ref(false)
let fetchInterval = null;

onMounted(() => {
	fetchDocuments();
	fetchInterval = setInterval(fetchDocuments, 10000);
});

onUnmounted(() => {
	if (fetchInterval) {
		clearInterval(fetchInterval);
	}
});

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

function download(jsonData, pdfname) {
	const filename = pdfname.replace(/\.pdf$/, '.docx');

	axios.post(import.meta.env.VITE_BACKEND_URL + '/generate_word', { jsonData, filename }, {
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

// State for delete confirmation dialog
const showDeleteDialog = ref(false);
const deleteTargetId = ref(null);
const deleteTargetName = ref('');

const confirmDelete = (id, name) => {
	deleteTargetId.value = id;
	deleteTargetName.value = name;
	showDeleteDialog.value = true;
};

const deleteItem = async () => {
	if (!deleteTargetId.value) return;
	try {
		const response = await axios.delete(`${import.meta.env.VITE_BACKEND_URL}/documents/${deleteTargetId.value}`);
		if (response.status === 200) {
			toast.showToast({ message: 'Document deleted successfully.' });
			fetchDocuments();
		}
	} catch (error) {
		console.error('Error deleting item:', error);
		toast.showToast({ message: 'Failed to delete document. Please try again.' });
	} finally {
		showDeleteDialog.value = false;
		deleteTargetId.value = null;
		deleteTargetName.value = '';
	}
};

const router = useRouter()
const toast = useToastStore()
const onRowClick = (item) => {
	if (item.status === 'failed' || item.status === 'in process') {
		toast.showToast({ message: `Item is ${item.status}. Please try again later or contact the team.` });
		return;
	}
	router.push({ name: 'doc-detail', params: { id: item.id } });
}

const showUploadDialog = ref(false);

const uploadFileKey = ref(1);
const onUploadDialogClose = () => {
	uploadFileKey.value++;
}

const onUploaded = () => fetchDocuments();

</script>

<template>
	<div class="flex justify-between mb-4">
		<h1 class="text-xl font-semibold">Documents</h1>
		<button class="px-3 py-2 bg-teal-500 text-white rounded-lg font-semibold" @click="showUploadDialog = true">
			Upload Paper
		</button>
	</div>
	<Dialog v-model="showUploadDialog" title="Upload Paper" size="fit-content" @on-close="onUploadDialogClose">
		<template #content>
			<UploadFile :key="uploadFileKey" @uploaded="onUploaded" />
		</template>
	</Dialog>
	<Dialog v-model="showDeleteDialog" title="Delete Document" size="fit-content">
		<template #content>
			<div>
				<p>Are you sure you want to delete <span class="font-semibold">{{ deleteTargetName }}</span>?</p>
			</div>
		</template>
		<template #footer>
			<div class="flex justify-end space-x-2">
				<button class="px-3 py-1 rounded-lg border border-gray-400 text-gray-700 hover:bg-gray-100"
					@click="showDeleteDialog = false">
					Cancel
				</button>
				<button class="px-3 py-1 rounded-lg border border-red-500 text-red-500 hover:text-white hover:bg-red-500"
					@click="deleteItem">
					Delete
				</button>
			</div>
		</template>
	</Dialog>
	<div class="bg-white rounded-lg p-4 border border-slate-300 shadow-sm">
		<Table class="overflow-y-auto h-[calc(100vh-150px)]" clickable-row :headers="headers" :data="tableData"
			@row-click="onRowClick" no-result-statement="No document found. Upload one to start" :loading="loading">
			<template #cell-content="{ rowData, header }">
				<div v-if="header.key === 'status'" class="px-2 py-1 w-fit rounded-full font-semibold text-xs border"
					:class="getStatusClass(rowData.status)">
					{{ rowData.status.toUpperCase() }}
				</div>
				<div v-else-if="header.key === 'uploaded_date'">
					{{ formatDate(rowData[header.key]) }}
				</div>
				<div v-else-if="header.key === 'actions'">
					<div class="flex justify-end space-x-2">
						<button v-if="rowData.status === 'extracted' || rowData.status === 'edited'"
							@click.stop="download(rowData.data, rowData.file_name)"
							class="px-2 py-1 rounded-lg border border-teal-500 text-teal-500 hover:text-white hover:bg-teal-500">
							Download
						</button>
						<button class="text-red-500 hover:text-white px-2 py-1 border border-red-500 hover:bg-red-500 rounded-lg"
							@click.stop="confirmDelete(rowData.id, rowData.file_name)">
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