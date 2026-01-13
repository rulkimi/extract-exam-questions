<script setup>
import { computed, provide, ref } from 'vue'
import ContentFlow from './ContentFlow.vue';
import MarksDisplay from './MarksDisplay.vue';

const props = defineProps({
  documentDetail: {
    type: Object,
    required: true
  },
  activeMainIndex: {
    type: Number,
    required: true
  },
  approvedCount: {
    type: Number,
    required: true
  },
  editable: {
    type: Boolean,
    default: true
  }
})

provide('imageData', computed(() => props.documentDetail?.image_data || []));

const emit = defineEmits(['approve-question', 'jump-to-page', 'update:document-detail'])

const containerRef = ref(null)

const totalMainQuestions = computed(() => props.documentDetail?.data?.main_questions?.length || 0)
const currentMainQuestion = computed(() => {
  const mqs = props.documentDetail?.data?.main_questions || []
  return mqs[props.activeMainIndex] || null
})

function approveQuestion() {
  emit('approve-question')
}

function jumpToStartPage(index) {
  emit('jump-to-page', index)
  // Scroll to top when clicking question button
  if (containerRef.value) {
    containerRef.value.scrollTop = 0
  }
}

function updateDocumentDetail(updatedDetail) {
  emit('update:document-detail', updatedDetail)
}

function updateContentFlow(contentIndex, newContent) {
  const updatedDetail = JSON.parse(JSON.stringify(props.documentDetail))
  updatedDetail.data.main_questions[props.activeMainIndex].content_flow[contentIndex] = newContent
  updateDocumentDetail(updatedDetail)
}

function updateQuestionContent(questionIndex, contentIndex, newContent) {
  const updatedDetail = JSON.parse(JSON.stringify(props.documentDetail))
  updatedDetail.data.main_questions[props.activeMainIndex].questions[questionIndex].content_flow[contentIndex] = newContent
  updateDocumentDetail(updatedDetail)
}

function updateSubQuestionContent(questionIndex, subQuestionIndex, contentIndex, newContent) {
  const updatedDetail = JSON.parse(JSON.stringify(props.documentDetail))
  updatedDetail.data.main_questions[props.activeMainIndex].questions[questionIndex].sub_questions[subQuestionIndex].content_flow[contentIndex] = newContent
  updateDocumentDetail(updatedDetail)
}
</script>

<template>
  <div class="border rounded-lg bg-white shadow flex flex-col" style="height: calc(100vh - 140px);">
    <div class="px-4 py-3 border-b flex items-center justify-between flex-shrink-0">
      <h2 class="font-medium">Extracted Questions</h2>
      <div class="flex items-center gap-2">
        <button v-for="i in totalMainQuestions" :key="i" @click="jumpToStartPage(i - 1)"
          class="h-8 w-8 rounded-md border text-sm"
          :class="activeMainIndex === i - 1 ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white hover:bg-gray-50'">
          {{ i }}
        </button>
      </div>
    </div>

    <div ref="containerRef" class="flex-1 p-4 space-y-4 overflow-auto">
      <div v-if="currentMainQuestion"
        class="text-left flex flex-col space-y-2">
        <div>Question {{ currentMainQuestion.number }}</div>
        <template v-for="(content, index) in currentMainQuestion.content_flow" :key="index">
          <ContentFlow :content="content" :editable="props.editable"
            @update:content="(newContent) => updateContentFlow(index, newContent)" />
        </template>


        <!-- display question -->
        <div v-for="(question, questionIndex) in currentMainQuestion.questions" :key="question.number"
          class="mb-4 flex flex-col">
          <div v-if="question.content_flow.length > 0" class="flex items-start">
            <!-- question number on the left -->
            <div v-if="question.number">{{ question.number.replace(/^\d+/, "") }}</div>
            <!-- all content flow items grouped on the right -->
            <div class="ml-2 flex-1 flex flex-col space-y-2">
              <template v-for="(content, index) in question.content_flow" :key="index">
                <ContentFlow :content="content" :editable="props.editable"
                  @update:content="(newContent) => updateQuestionContent(questionIndex, index, newContent)" />
              </template>

              <!-- display sub-questions nested within main question content -->
              <div v-for="(subQuestion, subQuestionIndex) in question.sub_questions" :key="subQuestion.number"
                class="flex flex-col">
                <div v-if="subQuestion.content_flow.length > 0" class="flex items-start">
                  <!-- sub-question number on the left -->
                  <div v-if="subQuestion.number">{{ subQuestion.number.match(/\([^)]*\)$/)?.[0] }}</div>
                  <!-- sub-question content flow on the right -->
                  <div class="ml-2 flex-1 flex flex-col space-y-2">
                    <template v-for="(content, index) in subQuestion.content_flow" :key="index">
                      <ContentFlow :content="content" :editable="props.editable"
                        @update:content="(newContent) => updateSubQuestionContent(questionIndex, subQuestionIndex, index, newContent)" />
                    </template>
                  </div>
                </div>

                <template v-if="subQuestion.marks" class="text-right">
                  <MarksDisplay :marks="subQuestion.marks" />
                </template>
              </div>
            </div>
          </div>
          <template v-else>
            <div class="flex items-start">
              <div>{{ question.number.replace(/^\d+/, "") }}</div>
              <div class="ml-2 flex-1 flex flex-col space-y-2">
                <!-- display sub-questions nested within main question content -->
                <div v-for="(subQuestion, subQuestionIndex) in question.sub_questions" :key="subQuestion.number"
                  class="flex flex-col">
                  <div v-if="subQuestion.content_flow.length > 0" class="flex items-start">
                    <!-- sub-question number on the left -->
                    <div v-if="subQuestion.number">{{ subQuestion.number.match(/\([^)]*\)$/)?.[0] }}</div>
                    <!-- sub-question content flow on the right -->
                    <div class="ml-2 flex-1 flex flex-col space-y-2">
                      <template v-for="(content, index) in subQuestion.content_flow" :key="index">
                        <ContentFlow :content="content" :editable="props.editable"
                          @update:content="(newContent) => updateSubQuestionContent(questionIndex, subQuestionIndex, index, newContent)" />
                      </template>
                    </div>
                  </div>

                  <template v-if="subQuestion.marks" class="text-right">
                    <MarksDisplay :marks="subQuestion.marks" />
                  </template>
                </div>
              </div>
            </div>
          </template>

          <template v-if="question.marks" class="text-right">
            <MarksDisplay :marks="question.marks" />
          </template>
        </div>

      </div>
      <div v-else class="text-center text-gray-500 italic">
        No question selected.
      </div>
    </div>
    <div class="p-2 border-t bg-white flex-shrink-0">
      <button @click="approveQuestion" class="w-full h-10 rounded-md bg-gray-900 text-white font-medium hover:bg-black transition-colors duration-200">
        <font-awesome-icon class="mr-2" :icon="['fas', 'check']" />
        Approve Question
      </button>
    </div>
  </div>
</template>
