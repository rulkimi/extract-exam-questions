<script setup>
import { computed, provide } from 'vue'
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
})

provide('imageData', computed(() => props.documentDetail?.image_data || []));

const emit = defineEmits(['approve-question', 'jump-to-page'])

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
}
</script>

<template>
  <div class="border rounded-lg bg-white shadow">
    <div class="px-4 py-3 border-b flex items-center justify-between">
      <h2 class="font-medium">Extracted Questions</h2>
      <div class="flex gap-2">
        <button v-for="i in totalMainQuestions" :key="i" @click="jumpToStartPage(i - 1)"
          class="h-8 w-8 rounded-md border text-sm"
          :class="activeMainIndex === i - 1 ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white hover:bg-gray-50'">
          {{ i }}
        </button>
      </div>
    </div>
    <!-- TODO: make sure to overflow -->
    <div class="p-4 space-y-4 overflow-auto" style="height: calc(100vh - 200px);">
      <div v-if="currentMainQuestion" class="border p-4 rounded-md bg-white shadow-md text-left flex flex-col">
        <div>Question {{ currentMainQuestion.number }}</div>
        <template v-for="(content, index) in currentMainQuestion.content_flow">
          <ContentFlow :content="content" />
        </template>
        

        <!-- display question -->
        <div v-for="question in currentMainQuestion.questions" :key="question.number" class="mb-4 flex flex-col">
          <!-- for each content flow items -->
          <template v-if="question.content_flow.length > 0" v-for="(content, index) in question.content_flow" >
            <!-- only add a number at the first content item  -->
            <div v-if="question.number && index === 0">
              {{ question.number.replace(/^\d+/, "") }}
            </div>
            <ContentFlow :content="content" />
          </template>
          <template v-else>
            {{ question.number.replace(/^\d+/, "") }}
          </template>

          <!-- show marks after content flow object -->
          <!-- TO-DO: make sure justify-right -->
          <template v-if="question.marks" class="text-right">
            <MarksDisplay :marks="question.marks" />
          </template>

          <!-- display sub-questions -->
          <div v-for="subQuestion in question.sub_questions" :key="subQuestion.number" class="ml-4 flex flex-col">
            <!-- for each content flow items -->
            <template v-for="(content, index) in subQuestion.content_flow">
              <!-- only add a number at the first content item  -->
              <div v-if="subQuestion.number && index === 0">
                {{ subQuestion.number.match(/\([^)]*\)$/)?.[0] }}
              </div>
              <ContentFlow :content="content" />
            </template>

            <!-- show marks after content flow object -->
            <!-- TO-DO: make sure justify-right -->
            <template v-if="subQuestion.marks" class="text-right">
              <MarksDisplay :marks="subQuestion.marks" />
            </template>
          </div>

        </div>

      </div>
      <div v-else class="text-center text-gray-500 italic">
        No question selected.
      </div>

      <div>
        <button @click="approveQuestion"
          class="w-full h-10 rounded-md bg-gray-900 text-white font-medium hover:bg-black">
          <font-awesome-icon class="mr-2" :icon="['fas', 'check']" />
          Approve Question
        </button>
      </div>
    </div>
  </div>
</template>
