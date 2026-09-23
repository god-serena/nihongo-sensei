<script setup lang="ts">
defineProps<{
  message: string;
}>();
</script>

<template>
  <Transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="transform translate-y-2 opacity-0"
    enter-to-class="transform translate-y-0 opacity-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="transform translate-y-0 opacity-100"
    leave-to-class="transform translate-y-2 opacity-0"
  >
    <div
      v-if="message"
      class="fixed bottom-6 right-6 z-50 flex items-center gap-2 bg-zinc-900 border border-emerald-500/40 text-emerald-400 px-4 py-3 rounded-xl shadow-2xl text-xs font-semibold"
    >
      <span>{{ message }}</span>
    </div>
  </Transition>
</template>
