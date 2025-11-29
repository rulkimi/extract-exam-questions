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
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { supabase } from '@/supabase'

const router = useRouter()
const hasRedirected = ref(false)

const upsertUserProfile = async (userData) => {
  console.log('Upserting user profile:', userData)
  const { data, error } = await supabase
    .from('profiles')
    .upsert({
      ...userData,
      updated_at: new Date().toISOString()
    })
    .select() // Add this to return the updated/inserted record
  
  console.log('Upsert result:', { data, error })
  
  if (error) {
    console.error('Error upserting profile:', error)
    throw error
  }
  
  return data
}

onMounted(async () => {
  console.log('OAuthCallback mounted, checking for session...');
  
  // Check for existing session
  const { data: { session: initialSession }, error: sessionError } = await supabase.auth.getSession();
  console.log('Initial session check:', { initialSession, sessionError });

  // Listen for auth state changes
  const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
    console.log('Auth state change:', { event, session });

    if (hasRedirected.value) {
      console.log('Already redirected, ignoring duplicate event');
      return;
    }

    if (event === 'SIGNED_IN' && session) {
      console.log('SIGNED_IN event received with session');
      hasRedirected.value = true;
      try {
        const { user } = session
        console.log('User signed in:', user)
        
        // Get user's full name from OAuth data
        const fullName = user.user_metadata?.full_name || 
                        user.user_metadata?.name ||
                        (user.user_metadata?.first_name && user.user_metadata?.last_name 
                          ? `${user.user_metadata.first_name} ${user.user_metadata.last_name}` 
                          : 'User')
        
        console.log('Upserting profile for OAuth user...')
        await upsertUserProfile({
          id: user.id,
          email: user.email,
          full_name: fullName
        })
        
        console.log('Profile updated, redirecting to app...')
        router.push({ name: 'doc-list' })
        
      } catch (error) {
        console.error('Error in auth state change handler:', error)
        errorMessage.value = "Failed to complete sign in. Please try again."
      }
    } else if (event === 'INITIAL_SESSION') {
      console.log('INITIAL_SESSION event:', { hasSession: !!session });
      if (session) {
        console.log('Session found on initial load');
        hasRedirected.value = true;
        try {
        const { user } = session
        console.log('User signed in:', user)
        
        // Get user's full name from OAuth data
        const fullName = user.user_metadata?.full_name || 
                        user.user_metadata?.name ||
                        (user.user_metadata?.first_name && user.user_metadata?.last_name 
                          ? `${user.user_metadata.first_name} ${user.user_metadata.last_name}` 
                          : 'User')
        
        console.log('Upserting profile for OAuth user...')
        await upsertUserProfile({
          id: user.id,
          email: user.email,
          full_name: fullName,
        })
        
        console.log('Profile updated, redirecting to app...')
        router.push({ name: 'doc-list' })
        
      } catch (error) {
        console.error('Error in auth state change handler:', error)
        error.value = "Failed to complete sign in. Please try again."
      }
      }
    }
  });

  onUnmounted(() => {
    console.log('OAuthCallback unmounting, cleaning up');
    subscription?.unsubscribe();
  });
});
</script>