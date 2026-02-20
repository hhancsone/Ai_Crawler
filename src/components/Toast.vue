<template>
  <div :class="['toast', show ? 'show' : '']">
    {{ message }}
  </div>
</template>

<script setup>
defineProps({
  message: String,
  show: Boolean
})

defineEmits(['hide'])
</script>
