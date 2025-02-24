<script setup>
import { ref } from "vue";

const isSidebarExpanded = ref(false);

const toggleSidebar = () => {
  isSidebarExpanded.value = !isSidebarExpanded.value;
};

</script>
<template>
  <nav
    class="sticky top-0 h-screen shrink-0 border-r border-slate-300 bg-white flex flex-col justify-between transition-all duration-300 overflow-hidden"
    :class="isSidebarExpanded ? 'w-[225px]' : 'w-[56px]' "
  >
  
    <div class="divide-y">
      <div class="flex items-center m-2 gap-3 cursor-pointer rounded-lg">
        <div class="size-10 p-3 flex items-center justify-center bg-teal-500 rounded-lg">
          <font-awesome-icon class="text-white" :icon="['fas', 'flask']" />
        </div>
        <div class="text-nowrap leading-none">
          <span class="block text-teal-500 font-semibold">EduWizard</span>
          <span class="text-slate-500 text-sm">Physics Paper 2</span>
        </div>
      </div>
      <div>
        <div class="flex items-center m-2 gap-3 cursor-pointer hover:bg-gray-100 rounded-lg">
          <div class="size-10 p-3 flex items-center justify-center">
            <font-awesome-icon class="text-slate-500" :icon="['fas', 'arrow-up-from-bracket']" />
          </div>
          <div class="text-nowrap text-slate-500">Upload Document</div>
        </div>
      </div>
    </div>

    <div class="flex items-center p-2 hover:bg-gray-200 border-t cursor-pointer" @click="toggleSidebar">
      <div class="size-10 flex items-center justify-center rounded-lg">
        <font-awesome-icon class="text-slate-500" :class="isSidebarExpanded ? 'rotate-180' : ''" :icon="['fas', 'chevron-right']" />
      </div>
      <div class="text-slate-500" v-if="isSidebarExpanded">Hide</div>
    </div>
  </nav>
</template>
