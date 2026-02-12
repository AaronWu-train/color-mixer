<template>
  <el-card shadow="hover" class="color-card">
    <div class="top">
      <div class="title">
        <div class="id">#{{ color?.id ?? '—' }}</div>
        <div class="name">{{ color?.name ?? 'Empty' }}</div>
      </div>

      <div class="swatch" :style="color ? { backgroundColor: rgbCss(color.rgb) } : {}" />
    </div>

    <div class="meta">
      <div class="rgb">rgb: {{ color ? color.rgb.join(', ') : '—' }}</div>
    </div>

    <div class="actions">
      <el-button type="primary" :disabled="!color" @click="onUse"> Dose 5 ml </el-button>
    </div>
  </el-card>
</template>

<script setup>
const props = defineProps({
  color: {
    type: Object, // { id: number, name: string, rgb: [number, number, number] } | null
    default: null,
  },
})

const emit = defineEmits(['use'])

function rgbCss(rgb) {
  const [r, g, b] = rgb
  return `rgb(${r}, ${g}, ${b})`
}

function onUse() {
  if (!props.color) return
  emit('use', props.color)
}
</script>

<style scoped>
.color-card {
  margin-bottom: 16px;
}
.top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.title .id {
  font-weight: 700;
  font-size: 14px;
  line-height: 1.2;
}
.title .name {
  font-size: 13px;
  opacity: 0.8;
}
.swatch {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.12);
}
.meta {
  margin-top: 10px;
  font-size: 12px;
  opacity: 0.8;
}
.actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}
</style>
