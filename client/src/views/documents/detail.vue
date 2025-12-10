<script setup>
import { useRoute } from 'vue-router';
import { ref, onMounted, computed, nextTick } from 'vue';
import PDFViewerWithNavigation from '@/components/PDFViewerWithNavigation.vue';
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
const topics = ref([])
const newTopic = ref('')
const pdfViewerRef = ref(null)

const totalMainQuestions = computed(() => documentDetail.value?.data?.main_questions?.length || 0)
const currentMainQuestion = computed(() => {
  const mqs = documentDetail.value?.data?.main_questions || []
  return mqs[activeMainIndex.value] || null
})
const currentQuestion = computed(() => {
  const mq = currentMainQuestion.value
  if (!mq) return null
  return Array.isArray(mq.questions) && mq.questions.length ? mq.questions[0] : null
})

const getFirstText = (flow) => {
  if (!Array.isArray(flow)) return ''
  for (const item of flow) {
    if (item?.type === 'text' && item?.text) {
      const malay = item.text.malay || ''
      const english = item.text.english || ''
      return [malay, english].filter(Boolean).join(' ').trim()
    }
  }
  return ''
}

const questionText = computed(() => {
  const mq = currentMainQuestion.value
  if (!mq) return ''
  if (currentQuestion.value?.content_flow) {
    const t = getFirstText(currentQuestion.value.content_flow)
    if (t) return t
  }
  return getFirstText(mq.content_flow)
})

const hasAnswerScheme = computed(() => !!documentDetail.value?.has_answer_scheme)

const fetchDocumentDetail = async () => {
  try {
    const response = await apiClient.get(`/documents/${props.id}`)
    const { data } = response.data
    documentDetail.value = data
    if (data?.subject) {
      topics.value = [data.subject]
    }
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

onMounted(() => {
  fetchDocumentDetail()
});
</script>

<template>
  <div class="p-6 space-y-4">
    <div class="flex justify-between items-center text-black">
      <router-link to="/list" class="font-medium hover:bg-gray-100 px-3 py-2 rounded-lg">
        <font-awesome-icon :icon="['fas', 'arrow-left']" class="mr-2" />
        Back to Dashboard
      </router-link>

      <div class="flex items-center flex-col">
        <h1 class="text-xl font-semibold">Review Your Paper</h1>
        <span class="text-gray-500">{{ approvedCount }} of {{ totalMainQuestions }} questions approved</span>
      </div>

      <button class="px-3 py-2 bg-gray-100 text-gray-800 rounded-lg font-semibold hover:bg-gray-200 border">
        <font-awesome-icon class="mr-2" :icon="['fas', 'check']" />
        Mark as Completed
      </button>
    </div>

    <div class="grid grid-cols-12 gap-6 text-black">
      <div :class="['col-span-12', hasAnswerScheme ? 'lg:col-span-3' : 'lg:col-span-5']">
        <div class="border rounded-lg bg-white shadow">
          <div class="px-4 py-3 border-b font-medium">Question Paper</div>
          <div class="p-4">
            <div v-if="documentDetail && documentDetail.file_url" class="h-[calc(100vh-260px)]">
              <PDFViewerWithNavigation
                ref="pdfViewerRef"
                :id="'qp-' + id"
                class="w-full h-full rounded-md border"
                :auto-fit="true"
                :file-name="documentDetail.file_name"
                :fileURL="documentDetail.file_url"
                />
            </div>
            <div v-else class="h-[calc(100vh-260px)] flex items-center justify-center rounded-md bg-gray-100 text-gray-400">
              PDF Preview
            </div>
          </div>
        </div>
      </div>

      <div :class="['col-span-12', hasAnswerScheme ? 'lg:col-span-6' : 'lg:col-span-7']">
        <div class="border rounded-lg bg-white shadow">
          <div class="px-4 py-3 border-b flex items-center justify-between">
            <h2 class="font-medium">Extracted Questions</h2>
            <div class="flex gap-2">
              <button
                v-for="i in totalMainQuestions"
                :key="i"
                @click="jumpToStartPage(i - 1)"
                class="h-8 w-8 rounded-md border text-sm"
                :class="activeMainIndex === i - 1 ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white hover:bg-gray-50'"
              >
                {{ i }}
              </button>
            </div>
          </div>
          <div class="p-4 space-y-6">
            <div>
              <div class="text-gray-700 font-medium">Question {{ currentMainQuestion?.number || activeMainIndex + 1 }}</div>
              <div class="mt-2 rounded-md bg-gray-100 text-gray-800 p-3">
                <div v-if="questionText">{{ questionText }}</div>
                <div v-else class="text-gray-400 italic">No extracted text available.</div>
              </div>
            </div>

            <div>
              <div class="text-gray-700 font-medium">Answer</div>
              <div class="mt-2 rounded-md bg-gray-100 text-gray-800 p-3">
                <div class="text-gray-600 italic">No answer provided.</div>
              </div>
            </div>

            <!-- <div>
              <div class="text-gray-700 font-medium">AI-Suggested Topics</div>
              <div class="mt-2 flex flex-wrap gap-2">
                <span
                  v-for="t in topics"
                  :key="t"
                  class="inline-flex items-center gap-2 px-2 py-1 rounded-full bg-gray-100 text-gray-700 border"
                >
                  {{ t }}
                  <button class="text-gray-500 hover:text-gray-700" @click="removeTopic(t)" aria-label="remove topic">
                    <font-awesome-icon :icon="['fas', 'xmark']" />
                  </button>
                </span>
              </div>
              <div class="mt-2 flex gap-2">
                <input
                  v-model="newTopic"
                  type="text"
                  placeholder="Add a topic..."
                  class="flex-1 h-10 rounded-md border px-3 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
                <button class="h-10 w-10 rounded-md border bg-white hover:bg-gray-50" @click="addTopic()">
                  <font-awesome-icon :icon="['fas', 'plus']" />
                </button>
              </div>
            </div> -->

            <div>
              <button @click="approveQuestion" class="w-full h-10 rounded-md bg-gray-900 text-white font-medium hover:bg-black">
                <font-awesome-icon class="mr-2" :icon="['fas', 'check']" />
                Approve Question
              </button>
            </div>
          </div>
        </div>
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