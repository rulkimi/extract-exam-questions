<template>
    <div class="relative">
        <button @click.stop="toggleMenu"
            class="profile-button w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center hover:bg-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            aria-haspopup="true" :aria-expanded="isOpen">
            <span class="sr-only">Open user menu</span>
            <font-awesome-icon :icon="['fas', 'user']" class="text-gray-600 text-sm" />
        </button>

        <transition enter-active-class="transition ease-out duration-100 transform"
            enter-from-class="opacity-0 scale-95" enter-to-class="opacity-100 scale-100"
            leave-active-class="transition ease-in duration-75 transform" leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95">
            <div v-if="isOpen" ref="menu"
                class="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg py-2 z-50 border border-gray-200"
                @click.stop>
                <!-- User info -->
                <div class="px-4 py-3 border-b border-gray-100">
                    <p class="text-sm font-medium text-gray-700">{{ user.name }}</p>
                    <p class="text-xs text-gray-500 truncate">{{ user.email }}</p>
                </div>

                <!-- Menu items -->
                <a href="#" class="flex items-center px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50">
                    <font-awesome-icon :icon="['far', 'user']" class="w-5 h-5 mr-3 text-gray-400" />
                    Profile
                </a>
                <a href="#" class="flex items-center px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50">
                    <font-awesome-icon :icon="['fas', 'cog']" class="w-5 h-5 mr-3 text-gray-400" />
                    Settings
                </a>
                <a href="#" class="flex items-center px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50">
                    <font-awesome-icon :icon="['far', 'question-circle']" class="w-5 h-5 mr-3 text-gray-400" />
                    Help Center
                </a>
                <a href="#" class="flex items-center px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50">
                    <font-awesome-icon :icon="['far', 'comment-alt']" class="w-5 h-5 mr-3 text-gray-400" />
                    Send Feedback
                </a>
                <div class="border-t border-gray-100 my-1"></div>
                <a href="#" class="flex items-center px-4 py-2.5 text-sm text-red-600 hover:bg-gray-50"
                    @click.prevent="handleLogout">
                    <font-awesome-icon :icon="['fas', 'right-from-bracket']" class="w-5 h-5 mr-3" />
                    Log Out
                </a>
            </div>
        </transition>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { supabase } from '@/supabase';
import { useToastStore } from '@/stores/toastStore';

const router = useRouter()
const toast = useToastStore()
const user = ref({
    name: 'User',
    email: ''
});

const emit = defineEmits(['logout']);

const isOpen = ref(false);
const menu = ref(null);

const toggleMenu = () => {
    isOpen.value = !isOpen.value;
};

const handleClickOutside = (event) => {
    const button = document.querySelector('.profile-button');
    if (!button || !menu.value) return;

    if (!button.contains(event.target) && !menu.value.contains(event.target)) {
        isOpen.value = false;
    }
};

const handleLogout = async () => {
    try {
        await supabase.auth.signOut();
        router.replace({ name: 'signin' });
    } catch (error) {
        console.error('Error signing out:', error);
        toast.error('Failed to sign out. Please try again.');
    }
};

onMounted(async () => {
    try {
        const { data: { session }, error } = await supabase.auth.getSession();
        if (error) throw error;
        if (!session) return;

        user.value = {
            name: session.user.user_metadata?.full_name ||
                session.user.user_metadata?.name ||
                session.user.email?.split('@')[0] ||
                'User',
            email: session.user.email || ''
        };
    } catch (error) {
        console.error('Error fetching user session:', error);
    }
    setTimeout(() => {
        document.addEventListener('click', handleClickOutside);
    }, 0);
});

onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside);
});
</script>