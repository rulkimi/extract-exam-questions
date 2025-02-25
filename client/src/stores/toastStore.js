import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useToastStore = defineStore('toast', () => {
  const toasts = ref([]);

  const MAX_TOASTS = 3;

  const showToast = ({ message, icon } = { message: 'Default message', icon: '' }) => {
    const toast = {
      id: Date.now(), 
      message,
      icon,
      isVisible: true,
      timeout: null,
    };

    if (toasts.value.length >= MAX_TOASTS) {
      const oldestToast = toasts.value.shift();
      if (oldestToast.timeout) clearTimeout(oldestToast.timeout);
    }

    toasts.value.push(toast);

    toast.timeout = setTimeout(() => {
      hideToast(toast.id);
    }, 5000);
  };

  const hideToast = (id) => {
    const index = toasts.value.findIndex((toast) => toast.id === id);
    if (index !== -1) {
      if (toasts.value[index].timeout) clearTimeout(toasts.value[index].timeout);
      toasts.value[index].isVisible = false;

      // Remove the toast from the list after a short delay to allow any exit animation
      setTimeout(() => {
        toasts.value.splice(index, 1);
      }, 300);
    }
  };

  return { toasts, showToast, hideToast };
});
