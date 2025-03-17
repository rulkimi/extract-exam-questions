<script setup>
import { useToastStore } from '@/stores/toastStore';

const toastStore = useToastStore();
</script>

<template>
  <transition name="appear" mode="out-in">
    <div
      v-if="toastStore.toasts.length"
      class="fixed bottom-0 right-0 m-6"
    >
      <transition-group name="list" tag="ul" class="flex flex-col gap-2">
        <li
          v-for="toast in toastStore.toasts"
          :key="toast.id"
          v-show="toast.isVisible"
          class="z-10 bg-white border p-4 shadow rounded-lg flex items-center gap-2 justify-between min-w-[300px] hover:shadow-lg transition-all duration-200"
        >
          <div class="flex items-center gap-2">
            <font-awesome-icon v-if="toast.icon" :icon="toast.icon" />
            <div>{{ toast.message }}</div>
          </div>
          <font-awesome-icon
            class="hover:scale-110 cursor-pointer"
            :icon="['fas', 'times']"
            @click="() => toastStore.hideToast(toast.id)"
          />
        </li>
      </transition-group>
    </div>
  </transition>
</template>

<style scoped>
.appear-enter-active, .appear-leave-active {
  transition: all 0.3s ease-out;
}
.appear-leave-to, .appear-enter-from {
  transform: translateY(100%);
  opacity: 0;
}
.appear-enter-to, .appear-leave-from {
  transform: translateY(0);
  opacity: 1;
}

.list-enter-active, .list-leave-active, .list-move {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.list-leave-active {
  position: relative;
}

.list-enter-from, .list-leave-to {
  transform: translateY(100%); 
  opacity: 0;
}
</style>
