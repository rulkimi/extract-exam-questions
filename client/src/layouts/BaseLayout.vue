<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import Sidebar from '@/components/Sidebar.vue';
import ProfileDropdown from '@/components/ProfileDropdown.vue';
import AlertToast from '@/components/AlertToast.vue';

const mobileMenuOpen = ref(false);
const router = useRouter();
</script>

<template>
  <div class="min-h-screen flex flex-col bg-white">
    <header class="sticky top-0 z-40 border-b border-gray-200 bg-white">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 py-3 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <router-link to="/" class="size-9 rounded-lg bg-indigo-500 flex items-center justify-center">
            <font-awesome-icon class="text-white" :icon="['fas', 'flask']" />
          </router-link>
          <span class="hidden md:inline text-gray-800 font-semibold">QPBank</span>
        </div>
        <div class="flex items-center gap-2">
          <button class="inline-flex md:hidden items-center justify-center h-9 w-9 rounded-lg bg-indigo-600 text-white"
                  @click="window.dispatchEvent(new CustomEvent('open-upload'))" aria-label="Upload">
            <font-awesome-icon :icon="['fas', 'plus']" />
          </button>
          <button class="inline-flex md:hidden items-center justify-center h-9 w-9 rounded-lg border text-gray-600"
                  @click="mobileMenuOpen = !mobileMenuOpen" aria-label="Open menu">
            <font-awesome-icon :icon="['fas', 'bars']" />
          </button>
          <nav class="hidden md:flex items-center gap-6">
            <router-link to="/list" class="text-gray-600 hover:text-gray-900">Documents</router-link>
            <router-link to="/settings" class="text-gray-600 hover:text-gray-900">Settings</router-link>
            <button class="px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700"
                    @click="window.dispatchEvent(new CustomEvent('open-upload'))">
              Upload Paper
            </button>
            <ProfileDropdown />
          </nav>
        </div>
      </div>
      <div v-if="mobileMenuOpen" class="md:hidden border-t border-gray-200 bg-white">
        <div class="mx-auto max-w-7xl px-4 sm:px-6 py-3 space-y-2">
          <router-link to="/list" class="block px-2 py-2 rounded hover:bg-gray-50 text-gray-700" @click="mobileMenuOpen=false">Documents</router-link>
          <router-link to="/settings" class="block px-2 py-2 rounded hover:bg-gray-50 text-gray-700" @click="mobileMenuOpen=false">Settings</router-link>
          <button class="w-full mt-2 px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium"
                  @click="window.dispatchEvent(new CustomEvent('open-upload')); mobileMenuOpen=false;">
            Upload Paper
          </button>
        </div>
      </div>
    </header>
    <div class="flex-grow w-full">
      <div class="flex">
        <!-- <Sidebar /> -->
        <div class="flex-grow max-h-screen mx-auto overflow-hidden">
          <RouterView></RouterView>
        </div>
      </div>
    </div>
  </div>
  <AlertToast />
</template>