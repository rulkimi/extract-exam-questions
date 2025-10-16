<!-- src/views/OAuthCallback.vue -->
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full space-y-8 p-8">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
        <h2 class="text-2xl font-bold text-gray-900">Completing Sign In</h2>
        <p class="mt-2 text-gray-600">Please wait while we complete your authentication...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { supabase } from '@/supabase'

const router = useRouter()

onMounted(async () => {
  try {
    // Get the current session to process the OAuth callback
    const { data: { session }, error } = await supabase.auth.getSession()

    if (error) {
      console.error('OAuth callback error:', error)
      router.push({
        name: 'signup',
        query: { error: 'oauth_failed', message: error.message }
      })
      return
    }

    if (session) {
      // Successfully signed in, redirect to main app
      console.log('OAuth successful, redirecting to app')
      router.push({ name: 'doc-list' })
    } else {
      // No session found, redirect back to signup
      console.warn('No session found after OAuth callback')
      router.push({ name: 'signup' })
    }
  } catch (error) {
    console.error('OAuth callback processing error:', error)
    router.push({
      name: 'signup',
      query: { error: 'oauth_processing_failed' }
    })
  }
})
</script>