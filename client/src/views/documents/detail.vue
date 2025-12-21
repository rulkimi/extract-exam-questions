<script setup>
import { useRoute } from 'vue-router';
import { ref, onMounted, computed, nextTick } from 'vue';
import PDFViewerWithNavigation from '@/components/PDFViewerWithNavigation.vue';
import ExtractedQuestions from '@/components/JsonEditor/Index.vue';
import apiClient from '@/api';

const documentDetail = ref(null)

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

const totalMainQuestions = computed(() => documentDetail.value?.data?.main_questions?.length || 0)
const hasAnswerScheme = computed(() => !!documentDetail.value?.has_answer_scheme)

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

  // Wait for the DOM update (if any)
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
        <div class="space-x-2 pr-4">
          <button class="px-3 py-2 text-gray-800 rounded-lg font-semibold hover:bg-gray-200">
            <font-awesome-icon :icon="['fas', 'undo']" />
          </button>
          <button class="px-3 py-2 text-gray-800 rounded-lg font-semibold hover:bg-gray-200">
            <font-awesome-icon :icon="['fas', 'redo']" />
          </button>
        </div>
        <div class="border-l pl-4 space-x-2">
          <button class="px-3 py-2 text-gray-800 rounded-lg font-semibold hover:bg-gray-200 border">
            <font-awesome-icon class="mr-2" :icon="['fas', 'floppy-disk']" />
            Save
          </button>
          <button class="px-3 py-2 text-gray-800 rounded-lg font-semibold hover:bg-gray-100 border">
            <font-awesome-icon class="mr-2" :icon="['fas', 'download']" />
            Export
          </button>
          <button class="px-3 py-2 bg-gray-500 text-white rounded-lg font-semibold hover:bg-gray-600 border">
            <font-awesome-icon class="mr-2" :icon="['fas', 'check']" />
            Completed
          </button>
        </div>
      </div>

    </div>

    <div class="grid grid-cols-12 gap-4 text-black">
      <div :class="['col-span-12', hasAnswerScheme ? 'lg:col-span-3' : 'lg:col-span-5']">
        <div class="border rounded-lg bg-white shadow">
          <div class="px-4 py-3 border-b font-medium">Question Paper</div>
          <div class="p-4">
            <div v-if="documentDetail && documentDetail.file_url" class="h-[calc(100vh-260px)]">
              <PDFViewerWithNavigation ref="pdfViewerRef" :id="'qp-' + id" class="w-full h-full rounded-md border"
                :auto-fit="true" :file-name="documentDetail.file_name" :fileURL="documentDetail.file_url" />
            </div>
            <div v-else
              class="h-[calc(100vh-260px)] flex items-center justify-center rounded-md bg-gray-100 text-gray-400">
              PDF Preview
            </div>
          </div>
        </div>
      </div>

      <div :class="['col-span-12', hasAnswerScheme ? 'lg:col-span-6' : 'lg:col-span-7']">
        <ExtractedQuestions :document-detail="documentDetail" :active-main-index="activeMainIndex"
          :approved-count="approvedCount" @approve-question="approveQuestion" @jump-to-page="jumpToStartPage" />
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
