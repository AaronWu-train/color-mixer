<template>
  <el-row :gutter="16">
    <el-col v-for="(item, idx) in cards" :key="idx" :xs="24" :sm="12" :md="8">
      <ColorCard :color="item" @use="(c) => emit('use', c)" />
    </el-col>
  </el-row>
</template>

<script setup>
import { computed } from 'vue'
import ColorCard from './ColorCard.vue'

const props = defineProps({
  colors: {
    type: Array,
    default: () => [],
  },
  count: {
    type: Number,
    default: 6,
  },
})

const emit = defineEmits(['use'])

const cards = computed(() => {
  const arr = [...props.colors]
  while (arr.length < props.count) arr.push(null)
  return arr.slice(0, props.count)
})
</script>
