<template>
  <section class="statistics-grid">
    <div class="statistics-layout">
      <StatisticsCard
        v-for="(card, idx) in cards"
        :key="idx"
        :title="card.title"
        :value="card.value"
      />
    </div>
  </section>
</template>

<script setup>
/* eslint-disable no-undef */
import { computed } from "vue";
import StatisticsCard from "./StatisticsCard.vue";

const props = defineProps({
  labels: { type: Array, required: true },
  values: { type: Array, required: true },
});

const cards = computed(() => {
  const total = props.values.reduce((sum, v) => sum + v, 0);
  const average = (total / props.values.length).toFixed(2);
  const maxIdx = props.values.indexOf(Math.max(...props.values));
  const minIdx = props.values.indexOf(Math.min(...props.values));
  return [
    { title: "Total de Auditorias Realizadas", value: total },
    { title: "Média de Auditorias", value: average },
    { title: "Área com Mais Auditorias", value: props.labels[maxIdx] },
    { title: "Área com Menos Auditorias", value: props.labels[minIdx] },
  ];
});
</script>

<style scoped>
.statistics-grid {
  margin-top: 16px;
  width: 100%;
}

.statistics-layout {
  display: flex;
  gap: 20px;
}
</style>
