<template>
  <div class="stat-card">
    <div class="stat-title">{{ title }}</div>
    <div class="stat-value">{{ value }}</div>
  </div>
</template>

<script>
export default {
  name: 'StatisticsCard',
  props: {
    title: { type: String, required: true },
    value: { type: [Number, String], required: true }
  }
};
</script>

<style scoped>
.stat-card {
  background: #fff;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.stat-title {
  font-size: 14px;
  color: #666;
}
.stat-value {
  margin-top: 4px;
  font-size: 24px;
  font-weight: bold;
}
</style>
