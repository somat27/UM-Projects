<template>
  <section class="statistics-grid">
    <div class="statistics-layout">
      <StatisticsCard v-for="(card, idx) in cards" :key="idx" :title="card.title" :value="formatValue(card.value)" />
    </div>
  </section>
</template>

<script>
import StatisticsCard from './StatisticsCard.vue';

export default {
  name: 'StatisticsGridOcorrencia',
  components: { StatisticsCard },
  props: {
    cards: {
      type: Array,
      required: true
    }
  },
  methods: {
    formatValue(val) {
      const num = parseFloat(val)
      if (!isNaN(num) && num === 0) {
        return '-'
      }
      return val
    }
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
