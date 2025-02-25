<script setup>
import ContentFlow from './ContentFlow.vue';
import MainQuestionContentFlow from './MainQuestionContentFlow.vue';
import MarksDisplay from './MarksDisplay.vue';

defineProps({
  sections: {
    type: Array,
    required: false
  }
});
</script>

<template>
  <div class="p-6 space-y-4 text-black">
    <div v-for="section in sections">
      <div class="space-y-8 mt-4">
        <template v-for="mainQuestion in section.main_questions" :key="mainQuestion.number">
          <div class="border p-4 rounded-md bg-white shadow-md text-left">
            <table class="w-full border-collapse border mt-2 bg-gray-50">
              <tbody>

                <!-- main questions -->
                <template
                  v-for="(content, index) in mainQuestion.content_flow"
                  :key="content.number"
                >
                  <MainQuestionContentFlow :content="content" :index="index" :number="mainQuestion.number" />
                  <tr v-if="mainQuestion.marks">
                    <td
                      colspan="4"
                      style="text-align: right; font-weight: bold"
                    >
                      <MarksDisplay :marks="mainQuestion.marks" />
                    </td>
                  </tr>
                </template>

                <!-- questions -->
                <template
                  v-for="question in mainQuestion.questions"
                  :key="question.number"
                >
                  <tr class="border bg-gray-100">
                    <td></td>
                    <td class="border p-2">
                      {{ question.number.replace(/^\d+/, "") }}
                    </td>
                    <td class="border p-2 space-y-6" colspan="2">
                      <template
                        v-for="content in question.content_flow"
                        :key="content.number"
                      >
                        <ContentFlow :content="content" />
                      </template>
                    </td>
                  </tr>
                  <tr v-if="question.marks" class="border bg-gray-100">
                    <td></td>
                    <td></td>
                    <td colspan="2" align="right">
                      <MarksDisplay :marks="question.marks" />
                    </td>
                  </tr>

                  <!-- sub questions -->
                  <template
                    v-for="subQuestion in question.sub_questions"
                    :key="subQuestion.number"
                  >
                    <tr class="border">
                      <td></td>
                      <td></td>
                      <td class="border p-2 pl-8">
                        {{ subQuestion.number.match(/\([^)]*\)$/)?.[0] }}
                      </td>
                      <td class="border p-2 space-y-6">
                        <template
                          v-for="content in subQuestion.content_flow"
                          :key="content.number"
                        >
                          <ContentFlow :content="content" />
                        </template>
                      </td>
                    </tr>
                    <tr v-if="subQuestion.marks" class="border bg-gray-100" align="right">
                      <td></td>
                      <td></td>
                      <td></td>
                      <td colspan="2">
                        <MarksDisplay :marks="subQuestion.marks" />
                      </td>
                    </tr>
                  </template>

                </template>
              </tbody>
            </table>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
th,
td {
  border: 1px solid black;
  padding: 8px;
  vertical-align: top;
}
</style>
