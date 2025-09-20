<template>
  <section class="statistics-grid">
    <div class="statistics-layout">
      <StatisticsCard v-for="(card, idx) in cards" :key="idx" :title="card.title" :value="card.value" />
    </div>
  </section>
</template>

<script>
import StatisticsCard from './StatisticsCard.vue';

export default {
  name: 'StatisticsGridMateriais',
  components: { StatisticsCard },
  props: {
    cards: { type: Array, required: true }
  }
};
</script>

<style scoped>
.statistics-grid {
  margin-top: 16px;
  width: 100%;
}

.statistics-layout {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
</style>
