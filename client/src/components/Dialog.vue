<script setup>
/*
    Example usage:

    <Dialog
        v-model="isDialogOpen"
        size="large"
        footerAlign="center"
        title="Example Dialog"
        @onClose="handleClose"
        @onOpen="handleOpen"
    >
        <template #title>
            <h3>Custom Title Slot</h3>
        </template>
        <template #content>
            <p>This is the content of the dialog.</p>
        </template>
        <template #footer>
            <button @click="isDialogOpen = false">Close</button>
            <button @click="handleSave">Save</button>
        </template>
    </Dialog>
*/
import { computed, onMounted, onBeforeUnmount, useSlots, nextTick, watch } from 'vue';

const emit = defineEmits(['update:modelValue', 'onClose', 'closed', 'onOpen']);

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  size: {
    type: String,
    default: 'regular',
    validator: value => ['small', 'large', 'regular', 'full', 'fit-content'].includes(value),
  },
  footerAlign: {
    type: String,
    default: 'left',
    validator: value => ['left', 'center', 'right'].includes(value),
  },
  title: {
    type: String,
    required: false,
    default: ''
  },
  disableBackgroundClick: {
    type: Boolean,
    default: false
  },
  showCloseBtn: {
    type: Boolean,
    default: true,
  },
  titleAlign: {
    type: String,
    default: 'between',
    validator: value => ['between', 'start', 'end', 'center'].includes(value),
  },
});

const slots = useSlots();

const hasTitle = computed(() => {
  return !!slots.title || props.title;
});

const hasFooter = computed(() => {
  return !!slots.footer;
});

const modalSize = computed(() => {
  switch (props.size) {
    case 'small':
      return 'w-11/12 md:w-1/4';
    case 'large':
      return 'w-11/12 md:w-3/4';
    case 'full':
      return 'w-full';
    case 'fit-content':
      return 'auto';
    default:
      return 'w-11/12 md:w-1/2';
  }
});

const footerAlignment = computed(() => {
  switch (props.footerAlign) {
    case 'left':
      return 'text-left';
    case 'right':
      return 'text-right';
    default:
      return 'text-center';
  }
});

const titleAlignment = computed(() => {
  switch (props.titleAlign) {
    case 'between':
      return 'justify-between';
    case 'start':
      return 'justify-start';
    case 'end':
      return 'justify-end';
    default:
      return 'justify-center';
  }
});

const handleKeydown = (event) => {
  if (event.key === 'Escape') {
    handleBackgroundClick();
  }
};

const onOpen = () => {
  emit('onOpen');
};

const onClose = () => {
  emit('onClose');
};

const handleBackgroundClick = () => {
  if (props.disableBackgroundClick) return;
  emit('update:modelValue', false);
};

const hanldeAfterLeave = () => {
  nextTick(() => {
    emit('closed');
  });
};

const hideContent = () => {
  setTimeout(() => {
    return props.modelValue;
  }, 300);
};

onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown);
});

// Watch for modelValue changes
watch(() => props.modelValue, (newValue) => {
  console.log('here')
  if (newValue) {
    onOpen();
  } else {
    onClose();
  }
});
</script>

<template>
  <!-- scrollable container for background -->
  <transition name="fade" @after-leave="hanldeAfterLeave">
    <div v-show="modelValue" class="fixed inset-0 z-[1000] overflow-auto">
      <!-- black background -->
      <div @click="handleBackgroundClick" class="fixed inset-0 bg-black bg-opacity-50 pointer-events-auto"></div>
      
      <transition name="offset">
        <div v-show="modelValue" class="flex justify-center items-center my-6 min-h-full">
          <div :class="modalSize" class="bg-white p-4 rounded-lg shadow-md flex flex-col relative custom-modal">
            <!-- Header -->
            <div
              v-if="hasTitle || showCloseBtn"
              class="flex items-center mb-4"
              :class="titleAlignment"
            >
              <div v-if="hasTitle">
                <slot name="title">
                  <h5 class="font-bold">{{ title }}</h5>
                </slot>
              </div>

              <div class="ml-4 self-start">
                <button @click="$emit('update:modelValue', false)" class="text-gray-600 hover:scale-110 transition-all duration-200" v-if="showCloseBtn">
                  <font-awesome-icon :icon="['fas', 'times']" />
                </button>
              </div>
            </div>

            <!-- Content -->
            <div v-if="hideContent" class="flex-1">
              <slot name="content"></slot>
            </div>

            <!-- Footer -->
            <div v-if="hasFooter" :class="footerAlignment" class="mt-4">
              <slot name="footer"></slot>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </transition>
</template>


<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.offset-enter-active, .offset-leave-active {
  transition: all 0.3s;
}
.offset-enter-from, .offset-leave-to {
  opacity: 0;
  transform: translateY(-50px);
}
</style>