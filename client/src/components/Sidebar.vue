<script setup>
import { onMounted, ref, nextTick, watch } from "vue";
import { useRouter, useRoute } from "vue-router";

const isSidebarExpanded = ref(false);

const toggleSidebar = () => {
  isSidebarExpanded.value = !isSidebarExpanded.value;
};

const menus = [
  { label: "Documents", url: "/docs", icon: ["far", "file"] },
  { label: "Playground", url: "/playground", icon: ["fas", "vial"] },
]
const router = useRouter();
const route = useRoute();

onMounted(() => {
  nextTick(() => {
    activeMenu.value = route.path;
  })
})

watch(route, (newRoute) => {
  activeMenu.value = newRoute.path;
});

const activeMenu = ref("/docs");
const setActiveMenu = (url) => {
  activeMenu.value = url;
  router.push(url);
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
      <div class="flex flex-col gap-1 py-2">
        <div
          v-for="menu in menus"
          :key="menu.url"
          class="flex items-center mx-2 gap-3 cursor-pointer rounded-lg border"
          :class="activeMenu.startsWith(menu.url) ? 'bg-teal-50 text-teal-500 shadow-sm border-teal-100' : 'text-slate-500 hover:bg-gray-100 border-transparent'"
          @click="setActiveMenu(menu.url)"
        >
          <div class="size-10 p-3 flex items-center justify-center">
            <font-awesome-icon
              :icon="menu.icon" 
            />
          </div>
          <div class="text-nowrap">
            {{ menu.label }}
          </div>
        </div>
      </div>
    </div>

    <div class="flex items-center p-2 hover:bg-gray-100 border-t cursor-pointer" @click="toggleSidebar">
      <div class="size-10 flex items-center justify-center rounded-lg">
        <font-awesome-icon class="text-slate-500" :class="isSidebarExpanded ? 'rotate-180' : ''" :icon="['fas', 'chevron-right']" />
      </div>
      <div class="text-slate-500" v-if="isSidebarExpanded">Hide</div>
    </div>
  </nav>
</template>
