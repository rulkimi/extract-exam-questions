<template>
  <div class="antialiased font-sans text-gray-900">
    <!-- Add a loading overlay -->
    <div v-if="loading" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div class="text-white text-xl">Signing in...</div>
    </div>
    <div class="gradient-bg min-h-screen flex items-center justify-center p-4">

      <div class="w-full max-w-md bg-white rounded-xl shadow-2xl p-8 space-y-6">

        <div class="text-center">
          <h1 class="text-3xl font-bold text-gray-800">Sign in</h1>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative"
          role="alert">
          <span class="block sm:inline">{{ errorMessage }}</span>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <label for="email" class="block text-sm font-semibold text-gray-700 mb-2">
              Email Address
            </label>
            <input v-model="email" type="email" id="email" name="email" placeholder="you@example.com" required
              class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
          </div>

          <div>
            <div class="flex justify-between items-center mb-2">
              <label for="password" class="block text-sm font-semibold text-gray-700">
                Password
              </label>
              <router-link to="/forgot-password" class="text-sm font-medium text-indigo-600 hover:text-indigo-500">
                Forgot password?
              </router-link>
            </div>
            <input v-model="password" type="password" id="password" name="password" required
              class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
          </div>

          <div>
            <button type="submit" :disabled="loading"
              class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors">
              Sign In
            </button>
          </div>

          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-300"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-2 bg-white text-gray-500">Or continue with</span>
            </div>
          </div>

          <button @click.prevent="signInWithGoogle" :disabled="loading"
            class="w-full flex items-center justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
            <img class="h-5 w-5 mr-2" src="https://www.svgrepo.com/show/475656/google-color.svg" alt="Google logo">
            Sign in with Google
          </button>
        </form>

        <p class="text-center text-sm text-gray-600">
          Don't have an account?
          <router-link to="/signup" class="font-medium text-indigo-600 hover:text-indigo-500">
            Sign up for free
          </router-link>
        </p>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { supabase } from '@/supabase'

// Reactive variables for form inputs
const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref(null)
const router = useRouter()

const handleLogin = async () => {
  try {
    loading.value = true
    errorMessage.value = null
    const { data, error } = await supabase.auth.signInWithPassword({
      email: email.value,
      password: password.value,
    })
    if (error) throw error
    router.push({ name: 'doc-list' })
  } catch (error) {
    errorMessage.value = error.error_description || error.message
  } finally {
    loading.value = false
  }
};

// const signInWithGoogle = async () => {
//   try {
//     loading.value = true
//     errorMessage.value = null
//     console.log(`window location origin: ${window.location.origin}`)
//     console.log(`import.meta.env.VITE_BASE_URL: ${import.meta.env.VITE_BASE_URL}`)

//     const { error } = await supabase.auth.signInWithOAuth({
//       provider: 'google',
//       options: {
//         // redirectTo: `${window.location.origin}${import.meta.env.VITE_BASE_URL || ''}/#/oauth-callback`,
//         redirectTo: `http://localhost:5173/extract-exam-questions/#/oauth-callback`,
//         // redirectTo: `https://fulwwvxvxcgpfcqthkkc.supabase.co/auth/v1/callback`,
//       }
//     })

//     if (error) throw error
//     // The redirect will happen automatically

//   } catch (error) {
//     errorMessage.value = error.message || "An error occurred during Google sign up"
//     loading.value = false
//   }
// }

const signInWithGoogle = async () => {
  try {
    loading.value = true;
    errorMessage.value = null;
    
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/oauth-callback`,
        queryParams: {
          access_type: 'offline',
          prompt: 'consent',
        }
      }
    });

    if (error) throw error;
  } catch (error) {
    errorMessage.value = error.message || "An error occurred during Google sign in";
    console.error('Google sign-in error:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  // This listener handles the redirect back from Google
  const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
    console.log('Auth state change:', event, session);

    if (event === 'SIGNED_IN') {
      // Only redirect if we're not already on the target page
      if (router.currentRoute.value.name !== 'doc-list') {
        await router.push({ name: 'doc-list' });
      }
    } else if (event === 'SIGNED_OUT') {
      // When user signs out, ensure they are on the landing or signin page
      if (router.currentRoute.value.name !== 'landing' && router.currentRoute.value.name !== 'signin') {
        await router.push({ name: 'signin' });
      }
    } else if (event === 'INITIAL_SESSION') {
      // Handle initial session
      if (session) {
        // User is already signed in, redirect to app
        if (router.currentRoute.value.name !== 'doc-list') {
          await router.push({ name: 'doc-list' });
        }
      }
    }
  });

  // Cleanup subscription on component unmount
  onUnmounted(() => {
    subscription?.unsubscribe();
  });
})
</script>

<style scoped>
/* Scoped styles allow you to keep component-specific CSS encapsulated.
   The gradient style is reused from the landing page for consistency.
*/
.gradient-bg {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>