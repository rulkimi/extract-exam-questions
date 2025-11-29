<script setup>
// Click outside directive
const vClickOutside = {
  beforeMount(el, binding) {
    el.clickOutsideEvent = function(event) {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value();
      }
    };
    document.addEventListener('click', el.clickOutsideEvent);
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent);
  },
};
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import apiClient from "@/api";
import { supabase } from "@/supabase";
import Table from '@/components/Table.vue';
import { formatDate } from "@/utils";
import { useToastStore } from "@/stores/toastStore";
import Dialog from "@/components/Dialog.vue";
import UploadFile from "@/components/UploadFile.vue";
import Spinner from "@/components/Spinner.vue";
import ProfileDropdown from '@/components/ProfileDropdown.vue';

const headers = [
  { key: 'file_name', label: 'File Name' },
  { key: 'subject', label: 'Subject' },
  { key: 'has_answer_scheme', label: 'Answer Scheme' },
  { key: 'uploaded_date', label: 'Uploaded' },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: 'Quick Actions', width: '200px' }
];
const tableData = ref([])
const loading = ref(false)
let subscription = null;

onMounted(async () => {
  // Ensure session is ready before fetching documents
  try {
    const { data: { session }, error } = await supabase.auth.getSession();
    if (error) {
      console.error('Session error:', error);
      router.push({ name: 'signin' });
      return;
    }
    if (!session) {
      console.warn('No active session found');
      router.push({ name: 'signin' });
      return;
    }
    await fetchDocuments();
    setupRealtimeSubscription();
  } catch (error) {
    console.error('Error checking session:', error);
    router.push({ name: 'signin' });
  }
});

// Clean up subscription when component is unmounted
onUnmounted(() => {
  if (subscription) {
    subscription.unsubscribe();
  }
});

const setupRealtimeSubscription = async () => {
  try {
    // Get the current session
    const { data: { session } } = await supabase.auth.getSession();
    if (!session?.user) {
      console.error('No active session found for real-time subscription');
      return;
    }

    console.log('Setting up real-time subscription for user:', session.user.id);
    console.log('session.user:', session.user)
    console.log('session.user.user_metadata:', session.user.user_metadata)

    // Create a channel for real-time updates
    subscription = supabase
      .channel('documents_changes')
      .on('postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'documents',
          filter: `user_id=eq.${session.user.id}`
        },
        (payload) => {
          console.log('Change received!', payload);
          fetchDocuments();
        }
      )
      .subscribe((status) => {
        console.log('Subscription status:', status);
        if (status === 'CHANNEL_ERROR') {
          console.error('Error with real-time subscription');
        }
      });

  } catch (error) {
    console.error('Error setting up real-time subscription:', error);
  }
};

const fetchDocuments = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get('/documents');
    const { data, message, status } = response.data;
    tableData.value = data.documents;
  } catch (error) {
    console.error('Error fetching documents:', error);
    toast.error('Failed to load documents');
  } finally {
    loading.value = false;
  }
}

const getStatusClass = (status) => {
  switch (status) {
    case 'in process':
      return 'border-yellow-500 text-yellow-500';
    case 'extracted':
      return 'border-indigo-500 text-indigo-500';
    case 'edited':
      return 'border-blue-500 text-blue-500';
    case 'failed':
      return 'border-red-500 text-red-500';
    default:
      return 'border-gray-400';
  }
};

const getSubjectClass = (subject) => {
  const colors = {
    'Physics': 'bg-blue-100 text-blue-800',
    'Mathematics': 'bg-red-100 text-red-800',
    'Chemistry': 'bg-green-100 text-green-800',
    'Biology': 'bg-green-100 text-green-800',
    'English': 'bg-purple-100 text-purple-800',
  };
  return colors[subject] || 'bg-gray-100 text-gray-800';
};

const formatStatus = (status) => {
  const statusMap = {
    'completed': 'Completed',
    'review_needed': 'Review Needed',
    'in process': 'In Process',
    'in_process': 'In Process',
    'failed': 'Failed',
    'extracted': 'Extracted'
  };
  return statusMap[status] || status;
};

const getStatusBadgeClass = (status) => {
  const classes = {
    'completed': 'bg-green-100 text-green-800',
    'review_needed': 'bg-yellow-100 text-yellow-800',
    'in_process': 'bg-blue-100 text-blue-800',
    'failed': 'bg-red-100 text-red-800',
    'extracted': 'bg-blue-100 text-blue-800',
  };
  return classes[status] || 'bg-gray-100 text-gray-800';
};

const handleReviewNow = (item) => {
  router.push({ name: 'doc-detail', params: { id: item.id } });
};

const handleViewEdit = (item) => {
  router.push({ name: 'doc-detail', params: { id: item.id } });
};

const handleDownload = (item) => {
  // Add your download logic here
  console.log('Download:', item);
};

const handleMore = (item) => {
  // Add your more options logic here
  console.log('More options:', item);
};

function download(jsonData, pdfname) {
  const filename = pdfname.replace(/\.pdf$/, '.docx');

  apiClient.post('/generate_word', { jsonData, filename }, {
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
    const response = await apiClient.delete(`/documents/${deleteTargetId.value}`);
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

const closeMenu = (event) => {
  // Prevent the click from propagating to the document
  event?.stopPropagation();
  showProfileMenu.value = false;
};

const onRowClick = (item) => {
  if (item.status === 'failed' || item.status === 'in process') {
    toast.showToast({ message: `Item is ${item.status}. Please try again later or contact the team.` });
    return;
  }
  router.push({ name: 'doc-detail', params: { id: item.id } });
}

const showUploadDialog = ref(false);
const showProfileMenu = ref(false);
const uploadFileKey = ref(1);

const handleOpenUpload = () => {
  showUploadDialog.value = true;
};

// Handle click outside using a more reliable method
const handleClickOutside = (event) => {
  const button = document.querySelector('.profile-button');
  const menu = document.querySelector('.profile-menu');
  
  if (button && menu && !button.contains(event.target) && !menu.contains(event.target)) {
    showProfileMenu.value = false;
  }
};

// Add event listener when component mounts
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  window.addEventListener('open-upload', handleOpenUpload);
});

// Clean up event listener when component is unmounted
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  window.removeEventListener('open-upload', handleOpenUpload);
  if (subscription) {
    subscription.unsubscribe();
  }
});

const onUploadDialogClose = () => {
  uploadFileKey.value++;
}

const onUploaded = () => {
  showUploadDialog.value = false;
  uploadFileKey.value++;
  fetchDocuments();
}
</script>

<template>
  <!-- Header -->
  <header class="hidden">
    <div class="mx-auto max-w-7xl px-6 py-4">
      <div class="flex justify-between items-center">
        <div class="flex items-center space-x-10">
          <h1 class="text-2xl font-bold text-gray-800">QPBank</h1>
          <!-- <nav class="flex space-x-8 text-gray-600">
            <router-link to="/documents" class="font-medium text-indigo-600 border-b-2 border-indigo-600 pb-2 px-1">
              My Documents
            </router-link>
            <router-link to="/question-bank" class="text-gray-500 hover:text-gray-700 pb-2 px-1">
              Question Bank
            </router-link>
          </nav> -->
        </div>
        <div class="flex items-center space-x-4 relative">
          <button
            class="px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium flex items-center hover:bg-indigo-700 transition-colors text-sm"
            @click="showUploadDialog = true">
            <font-awesome-icon :icon="['fas', 'upload']" class="mr-2" />
            Upload Paper
          </button>
          <ProfileDropdown />
        </div>
      </div>
    </div>
  </header>

  <!-- Description -->
  <div class="border-b border-gray-200">
    <div class="mx-auto max-w-7xl px-6 py-4">
      <h2 class="text-xl font-semibold text-gray-800">My Documents</h2>
      <p class="text-gray-500 text-sm mt-1">Manage and review your exam papers</p>
    </div>
  </div>

  <!-- Search and Filters -->
  <div class="border-b border-gray-200">
    <div class="mx-auto max-w-7xl px-6 py-4">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="relative flex-1 max-w-md">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <font-awesome-icon :icon="['fas', 'search']" class="text-gray-400 text-sm" />
          </div>
          <input type="text"
            class="block w-full pl-10 pr-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Search by name..." />
        </div>
        <button class="md:hidden inline-flex items-center justify-center gap-2 h-9 px-3 border rounded-lg text-sm text-gray-700">
          <font-awesome-icon :icon="['fas', 'sliders-h']" />
          Filters
        </button>

        <div class="hidden md:flex flex-wrap gap-2">
          <select
            class="text-xs border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 h-9">
            <option>All Subjects</option>
            <option>Physics</option>
            <option>Mathematics</option>
            <option>Chemistry</option>
            <option>Biology</option>
            <option>English</option>
          </select>

          <select
            class="text-xs border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 h-9">
            <option>All Statuses</option>
            <option>Completed</option>
            <option>Review Needed</option>
          </select>

          <select
            class="text-xs border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 h-9">
            <option>All Documents</option>
            <option>PDF</option>
            <option>DOCX</option>
          </select>

          <select
            class="text-xs border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 h-9">
            <option>Date (Newest)</option>
            <option>Date (Oldest)</option>
          </select>
        </div>
      </div>
    </div>
  </div>

  <!-- Documents Table -->
  <div class="bg-gray-50 min-h-screen flex flex-col">
    <div class="mx-auto max-w-7xl px-6 py-4">
      <div class="bg-white rounded-lg border border-gray-200 p-4 mb-6">
        <div class="overflow-x-auto hidden md:block">
          <div class="flex justify-between items-center mb-3">
            <h3 class="text-sm font-medium text-gray-700">Documents</h3>
            <span class="text-xs text-gray-500">{{ tableData.length }} of {{ tableData.length }} documents</span>
          </div>

          <!-- add @row-click="onRowClick" for row click -->
          <Table class="w-full hover:shadow-md" :headers="headers" :data="tableData"
            :loading="loading" :clickableRow="true" no-result-statement="No documents found. Upload one to get started.">
          
            <template #cell-content="{ rowData, header }">
              <!-- File Name -->
              <div v-if="header.key === 'file_name'" class="text-sm font-normal text-gray-900">
                {{ rowData.file_name }}
              </div>

              <!-- Subject -->
              <div v-else-if="header.key === 'subject'" class="inline-flex">
                <span class="px-2.5 py-0.5 rounded-full text-xs font-medium" :class="getSubjectClass(rowData.subject)">
                  {{ rowData.subject }}
                </span>
              </div>

              <!-- Answer Scheme -->
              <div v-else-if="header.key === 'has_answer_scheme'" class="flex items-center">
                <span v-if="rowData.has_answer_scheme" class="text-green-600 text-sm">
                  <font-awesome-icon :icon="['fas', 'check-circle']" class="mr-1" />
                  Yes
                </span>
                <span v-else class="text-gray-400 text-sm">No</span>
              </div>

              <!-- Uploaded Date -->
              <div v-else-if="header.key === 'uploaded_date'" class="text-sm text-gray-500">
                {{ formatDate(rowData.uploaded_date) }}
              </div>

              <!-- Status -->
              <div v-else-if="header.key === 'status'" class="flex items-center">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="getStatusBadgeClass(rowData.status)">
                  <font-awesome-icon v-if="rowData.status === 'completed'" :icon="['fas', 'check']"
                    class="mr-1 text-xs" />
                  <font-awesome-icon v-else-if="rowData.status === 'review_needed'" :icon="['fas', 'sync']"
                    class="mr-1 text-xs animate-spin" />
                  {{ formatStatus(rowData.status) }}
                </span>
              </div>

              <!-- Actions -->
              <div v-else-if="header.key === 'actions'" class="flex items-center space-x-2">
                <button v-if="rowData.status === 'review_needed'" @click.stop="handleReviewNow(rowData)"
                  class="px-3 py-1 bg-indigo-600 text-white text-xs font-medium rounded hover:bg-indigo-700 transition-colors">
                  Review Now
                </button>
                <div class="flex space-x-1">
                  <button @click.stop="handleViewEdit(rowData)"
                    class="py-1.5 px-3 border text-gray-500 hover:text-gray-600 hover:bg-gray-200 rounded-lg" title="View/Edit">
                    <font-awesome-icon :icon="['far', 'edit']" class="text-sm" />
                    View/Edit
                  </button>
                  <button @click.stop="handleDownload(rowData)"
                    class="py-1.5 px-3 border text-gray-500 hover:text-gray-600 hover:bg-gray-200 rounded-lg" title="Download">
                    <font-awesome-icon :icon="['far', 'arrow-alt-circle-down']" class="text-sm" />
                  </button>
                  <button @click.stop="handleMore(rowData)"
                    class="py-1.5 px-3 text-gray-500 hover:text-gray-600"
                    title="More options">
                    <font-awesome-icon :icon="['fas', 'ellipsis-v']" class="text-sm" />
                  </button>
                </div>
              </div>
            </template>
          </Table>
        </div>

        <!-- Mobile Cards -->
        <div class="md:hidden">
          <div class="flex justify-between items-center mb-3">
            <h3 class="text-sm font-medium text-gray-700">Documents</h3>
            <span class="text-xs text-gray-500">{{ tableData.length }} of {{ tableData.length }} documents</span>
          </div>
          <div v-if="loading" class="py-8 flex justify-center"><Spinner /></div>
          <div v-else>
            <div v-if="tableData.length === 0" class="text-sm text-gray-500 py-6 text-center">No documents found. Upload one to get started.</div>
            <div v-else class="space-y-4">
              <div v-for="item in tableData" :key="item.id" class="rounded-xl border border-gray-200 p-4">
                <div class="flex items-start justify-between">
                  <div class="min-w-0">
                    <div class="text-gray-900 font-medium truncate">{{ item.file_name }}</div>
                    <div class="mt-2 flex flex-wrap items-center gap-2 text-xs">
                      <span class="px-2.5 py-0.5 rounded-full font-medium" :class="getSubjectClass(item.subject)">{{ item.subject }}</span>
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full font-medium" :class="getStatusBadgeClass(item.status)">
                        <font-awesome-icon v-if="item.status === 'completed'" :icon="['fas', 'check']" class="mr-1 text-xs" />
                        <font-awesome-icon v-else-if="item.status === 'review_needed'" :icon="['fas', 'sync']" class="mr-1 text-xs animate-spin" />
                        {{ formatStatus(item.status) }}
                      </span>
                      <span v-if="item.has_answer_scheme" class="text-green-600 inline-flex items-center">
                        <font-awesome-icon :icon="['fas', 'check-circle']" class="mr-1" />
                        Has Answer Scheme
                      </span>
                      <span v-else class="text-gray-500">No Answer Scheme</span>
                    </div>
                  </div>
                  <button @click.stop="handleMore(item)" class="h-8 w-8 flex items-center justify-center text-gray-400 hover:text-gray-600">
                    <font-awesome-icon :icon="['fas', 'ellipsis-v']" />
                  </button>
                </div>
                <div class="mt-2 text-xs text-gray-500">{{ formatDate(item.uploaded_date) }}</div>

                <div class="mt-4 flex items-center gap-2">
                  <button v-if="item.status === 'review_needed'" @click="handleReviewNow(item)" class="flex-1 h-9 rounded-lg bg-indigo-600 text-white text-sm font-medium">Review Now</button>
                  <template v-else>
                    <button @click="handleViewEdit(item)" class="flex-1 h-9 rounded-lg border text-gray-700 text-sm">View / Edit</button>
                    <button @click="handleDownload(item)" class="h-9 w-9 rounded-lg border text-gray-600 flex items-center justify-center">
                      <font-awesome-icon :icon="['far', 'arrow-alt-circle-down']" />
                    </button>
                  </template>
                </div>

                <button v-if="!item.has_answer_scheme" class="mt-3 w-full h-9 rounded-lg border border-indigo-300 text-indigo-600 text-sm" @click="showUploadDialog = true">
                  + Upload Answer Scheme
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>


  <!-- Upload Dialog -->
  <Dialog v-model="showUploadDialog" title="Upload Exam Paper" size="fit-content" @on-close="onUploadDialogClose">
    <template #content>
      <UploadFile :key="uploadFileKey" @uploaded="onUploaded" @cancel="showUploadDialog = false" />
    </template>
  </Dialog>
</template>