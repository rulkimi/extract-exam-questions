<script setup>
const props = defineProps({
  row: {
    type: Object,
    required: true
  }
});
</script>

<template>
  <tr class="border">
    <td v-for="(cell, index) in props.row.cells" :key="index" class="border p-2" :colspan="cell.colspan || 1" :rowspan="cell.rowspan || 1">
      <div v-html="cell.text.malay || cell.text.english"></div>
    </td>
  </tr>
</template>
