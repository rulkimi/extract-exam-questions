<script setup>
import { computed } from 'vue'

const props = defineProps({
  content: {
    type: Object,
    required: true
  },
  editable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:content'])

const localContent = computed({
  get: () => props.content,
  set: (value) => emit('update:content', value)
})

function updateMalayText(value) {
  emit('update:content', {
    ...props.content,
    text: {
      ...props.content.text,
      malay: value
    }
  })
}

function updateEnglishText(value) {
  emit('update:content', {
    ...props.content,
    text: {
      ...props.content.text,
      english: value
    }
  })
}
</script>

<template>
  <div class="p-4 bg-gray-100 rounded-md">
    <div v-if="props.editable" class="space-y-2">
      <div>
        <label class="text-xs font-medium text-gray-700">Malay:</label>
        <textarea 
          v-model="props.content.text.malay"
          @input="updateMalayText($event.target.value)"
          class="w-full p-2 border rounded-md text-sm resize-none"
          rows="3"
          placeholder="Malay text..."
        ></textarea>
      </div>
      <div>
        <label class="text-xs font-medium text-gray-700">English:</label>
        <textarea 
          v-model="props.content.text.english"
          @input="updateEnglishText($event.target.value)"
          class="w-full p-2 border rounded-md text-sm resize-none italic text-gray-600"
          rows="2"
          placeholder="English text..."
        ></textarea>
      </div>
    </div>
    <div v-else>
      <div v-if="props.content.text.malay" v-html="props.content.text.malay"></div>
      <div v-if="props.content.text.english" class="mt-2 italic text-gray-600" v-html="props.content.text.english"></div>
    </div>
  </div>
</template>
