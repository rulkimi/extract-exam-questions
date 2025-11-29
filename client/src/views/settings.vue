<script setup>
import { supabase } from '@/supabase'
import router from '@/routers'

const checkUser = async () => {
  const { data: { session } } = await supabase.auth.getSession()
  console.log(session)
};

const signout = async () => {
  const { error } = await supabase.auth.signOut()
  if (error) {
    console.log(error)
    return
  }
  router.push({ name: 'landing' })
}

</script>
<template>
  <div class="flex h-full w-full">
    <div>
      <p>this is settings page</p>
      <button class="bg-indigo-500 text-white px-4 py-2 m-2 rounded" @click="checkUser">check user</button>
      <button class="bg-indigo-500 text-white px-4 py-2 rounded" @click="signout">sign out</button>
    </div>
  </div>
</template>