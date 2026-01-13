<script setup>
import { useRoute } from 'vue-router';
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue';
import PDFViewerWithNavigation from '@/components/PDFViewerWithNavigation.vue';
import ExtractedQuestions from '@/components/JsonEditor/Index.vue';
import apiClient from '@/api';

const documentDetail = ref(null)
const isSaving = ref(false)
const saveStatus = ref('')

const props = defineProps({
  id: {
    type: String,
    required: true
  }
})

// UI state
const activeMainIndex = ref(0)
const approvedCount = ref(0)
const pdfViewerRef = ref(null)
const isEditMode = ref(false)

const fileURL = computed(() => documentDetail.value?.file_url || '')
const fileName = computed(() => documentDetail.value?.file_name || '')
// Undo/Redo state
const documentHistory = ref([])
const currentHistoryIndex = ref(-1)
const MAX_HISTORY = 50 // Maximum number of history states to keep
const changeTimeout = ref(null)
const lastChangeTime = ref(0)
const CHANGE_DEBOUNCE = 1000 // 1 second debounce for grouping changes

const totalMainQuestions = computed(() => documentDetail.value?.data?.main_questions?.length || 0)
const hasAnswerScheme = computed(() => !!documentDetail.value?.has_answer_scheme)

function getQuestionStartPage(index) {
  const mqs = documentDetail.value?.data?.main_questions || []
  return parseInt(mqs[index]?.start_page, 10) || null
}

function toggleEditMode() {
  if (!isEditMode.value) {
    // When entering edit mode, save current state
    saveToHistory()
  } else {
    // When exiting edit mode, clear history
    documentHistory.value = []
    currentHistoryIndex.value = -1
  }
  isEditMode.value = !isEditMode.value
}

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

// Save current state to history with debouncing
function saveToHistory() {
  // Don't save if we're not in edit mode
  if (!isEditMode.value) return
  
  // Clear any pending saves
  if (changeTimeout.value) {
    clearTimeout(changeTimeout.value)
  }
  
  const now = Date.now()
  const timeSinceLastChange = now - lastChangeTime.value
  
  // If it's been a while since the last change, save immediately
  if (timeSinceLastChange > CHANGE_DEBOUNCE) {
    _saveToHistory()
  } else {
    // Otherwise, debounce to group rapid changes
    changeTimeout.value = setTimeout(() => {
      _saveToHistory()
    }, CHANGE_DEBOUNCE)
  }
  
  lastChangeTime.value = now
}

// Internal function to actually save the history
function _saveToHistory() {
  // Don't save if we're not in edit mode
  if (!isEditMode.value) return
  
  // Create a deep copy of the current document data
  const snapshot = JSON.parse(JSON.stringify(documentDetail.value))
  
  // Don't save if nothing has changed
  if (documentHistory.value.length > 0) {
    const lastState = documentHistory.value[currentHistoryIndex.value]
    if (JSON.stringify(lastState) === JSON.stringify(snapshot)) {
      return
    }
  }
  
  // If we're not at the end of history, remove the future history
  if (currentHistoryIndex.value < documentHistory.value.length - 1) {
    documentHistory.value = documentHistory.value.slice(0, currentHistoryIndex.value + 1)
  }
  
  // Add new state to history
  documentHistory.value.push(snapshot)
  currentHistoryIndex.value = documentHistory.value.length - 1
  
  // Limit history size
  if (documentHistory.value.length > MAX_HISTORY) {
    documentHistory.value.shift()
    currentHistoryIndex.value--
  }
}

// Undo to previous state
function undo() {
  if (currentHistoryIndex.value > 0) {
    currentHistoryIndex.value--
    documentDetail.value = JSON.parse(JSON.stringify(documentHistory.value[currentHistoryIndex.value]))
  }
}

// Redo to next state
function redo() {
  if (currentHistoryIndex.value < documentHistory.value.length - 1) {
    currentHistoryIndex.value++
    documentDetail.value = JSON.parse(JSON.stringify(documentHistory.value[currentHistoryIndex.value]))
  }
}

// Reset to last saved state
function resetToLastSaved() {
  if (documentHistory.value.length > 0) {
    documentDetail.value = JSON.parse(JSON.stringify(documentHistory.value[0]))
    documentHistory.value = []
    currentHistoryIndex.value = -1
  }
  isEditMode.value = false
}

const saveDocumentDetail = async () => {
  if (isSaving.value) return

  isSaving.value = true
  saveStatus.value = 'Saving...'

  try {
    const response = await apiClient.put(`/documents/${props.id}`, {
      data: documentDetail.value.data
    });

    saveStatus.value = 'Saved successfully!'
    setTimeout(() => {
      saveStatus.value = ''
    }, 3000)
    
    // After saving, clear history and exit edit mode
    documentHistory.value = []
    currentHistoryIndex.value = -1
    isEditMode.value = false
  } catch (error) {
    console.error('Error saving document:', error)
    saveStatus.value = 'Error saving document'
    setTimeout(() => {
      saveStatus.value = ''
    }, 3000)
  } finally {
    isSaving.value = false
  }
}

function updateDocumentDetail(updatedDetail) {
  documentDetail.value = updatedDetail
  saveToHistory()
}

// Clean up any pending timeouts when component is unmounted
onUnmounted(() => {
  if (changeTimeout.value) {
    clearTimeout(changeTimeout.value)
  }
})

function download(jsonData, pdfname) {
  const filename = pdfname.replace(/\.pdf$/, '.docx');
  const imageData = documentDetail.value?.image_data;
  console.log('downloading...')

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

function approveQuestion() {
  if (approvedCount.value < totalMainQuestions.value) {
    approvedCount.value += 1
  }
}

function addTopic() {
  const t = newTopic.value.trim()
  if (t && !topics.value.includes(t)) topics.value.push(t)
  newTopic.value = ''
}

function removeTopic(t) {
  topics.value = topics.value.filter(x => x !== t)
}

async function jumpToStartPage(index) {
  activeMainIndex.value = index

  const mqs = documentDetail.value?.data?.main_questions || []
  const startPage = parseInt(mqs[index]?.start_page, 10)
  // Check if the page is valid
  if (!startPage || startPage < 1) return

  // Wait for the DOM update
  await nextTick()

  const instance = pdfViewerRef.value
  if (!instance) return

  // Call the exposed method on the PDFViewerWithNavigation instance
  if (typeof instance.handleInputPageChanged === 'function') {
    instance.handleInputPageChanged(startPage)
  }
}

function selectQuestion(index) {
  activeQuestionIndex.value = index
}

onMounted(() => {
  fetchDocumentDetail()
});
</script>

<template>
  <div class="p-4 space-y-4">
    <!-- Top Navbar -->
    <div class="flex items-center justify-between text-black">
      <div class="flex gap-12">
        <router-link to="/list" class="font-medium hover:bg-gray-100 px-3 py-2 rounded-lg">
          <font-awesome-icon :icon="['fas', 'arrow-left']" class="mr-2" />
          Back
        </router-link>

        <div class="flex flex-col ">
          <h1 class="text-xl font-semibold">Review Your Paper</h1>
          <span class="text-gray-500">{{ approvedCount }} of {{ totalMainQuestions }} questions approved</span>
        </div>
      </div>

      <div class="flex">
        <div v-if="isEditMode" class="space-x-2 pr-4 border-r">
          <button 
            @click="undo" 
            :disabled="currentHistoryIndex <= 0"
            :class="[
              'px-3 py-2 rounded-lg font-semibold',
              currentHistoryIndex <= 0 
                ? 'text-gray-400' 
                : 'text-gray-800 hover:bg-gray-200'
            ]"
            :title="currentHistoryIndex <= 0 ? 'Nothing to undo' : 'Undo'"
          >
            <font-awesome-icon :icon="['fas', 'undo']" />
          </button>
          <button 
            @click="redo"
            :disabled="currentHistoryIndex >= documentHistory.length - 1"
            :class="[
              'px-3 py-2 rounded-lg font-semibold',
              currentHistoryIndex >= documentHistory.length - 1 
                ? 'text-gray-400' 
                : 'text-gray-800 hover:bg-gray-200'
            ]"
            :title="currentHistoryIndex >= documentHistory.length - 1 ? 'Nothing to redo' : 'Redo'"
          >
            <font-awesome-icon :icon="['fas', 'redo']" />
          </button>
        </div>
        <div class="pl-4 space-x-2">
          <button v-if="!isEditMode" @click="toggleEditMode"
            class="px-3 py-2 text-gray-800 border rounded-lg font-semibold hover:bg-gray-200">
            <font-awesome-icon :icon="['fas', 'edit']" />
            Edit
          </button>
          <button v-if="isEditMode" @click="saveDocumentDetail" :disabled="isSaving"
            class="px-3 py-2 text-gray-800 rounded-lg font-semibold hover:bg-gray-200 border disabled:opacity-50 disabled:cursor-not-allowed relative">
            <font-awesome-icon class="mr-2" :icon="['fas', 'floppy-disk']" />
            {{ isSaving ? 'Saving...' : 'Save' }}
            <span v-if="saveStatus" :class="[
              'absolute -top-8 left-1/2 transform -translate-x-1/2 px-2 py-1 text-xs rounded whitespace-nowrap',
              saveStatus.includes('Error') ? 'bg-red-500 text-white' : 'bg-green-500 text-white'
            ]">
              {{ saveStatus }}
            </span>
          </button>
          <button v-if="isEditMode" @click="resetToLastSaved"
            class="px-3 py-2 text-gray-800 rounded-lg font-semibold hover:bg-gray-200 border">
            Cancel
          </button>
          <button v-if="!isEditMode" class="px-3 py-2 text-gray-800 rounded-lg font-semibold hover:bg-gray-100 border"
            @click="download(documentDetail?.data, fileName)">
            <font-awesome-icon class="mr-2" :icon="['fas', 'download']" />
            Export
          </button>
          <button v-if="!isEditMode"
            class="px-3 py-2 bg-gray-500 text-white rounded-lg font-semibold hover:bg-gray-600 border">
            <font-awesome-icon class="mr-2" :icon="['fas', 'check']" />
            Completed
          </button>
        </div>
      </div>

    </div>

    <!-- Content -->
    <div class="grid grid-cols-12 gap-4 text-black">

      <PDFViewerWithNavigation ref="pdfViewerRef" :id="'qp-' + id" class="w-full h-full" :auto-fit="true"
        :file-name="fileName" :fileURL="fileURL"
        :gotoPage="getQuestionStartPage(activeMainIndex)" />


      <div :class="['col-span-12', hasAnswerScheme ? 'lg:col-span-6' : 'lg:col-span-6']">
        <ExtractedQuestions :document-detail="documentDetail" :active-main-index="activeMainIndex"
          :approved-count="approvedCount" :editable="isEditMode" @approve-question="approveQuestion"
          @jump-to-page="jumpToStartPage" @update:document-detail="updateDocumentDetail" />
      </div>

      <div v-if="hasAnswerScheme" class="col-span-12 lg:col-span-3">
        <div class="border rounded-lg bg-white shadow">
          <div class="px-4 py-3 border-b font-medium">Answer Scheme</div>
          <div class="p-4">
            <div class="h-[calc(100vh-260px)] flex items-center justify-center rounded-md bg-gray-100 text-gray-400">
              PDF Preview
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
