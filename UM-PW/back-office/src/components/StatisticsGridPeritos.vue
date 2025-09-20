<template>
  <section class="statistics-grid" :space="62">
    <div class="statistics-layout">
      <slot />
    </div>
  </section>
</template>

<script>
</script>

<style scoped>
.statistics-grid {
  width: 100%;
  max-width: 1036px;
}

.statistics-layout {
  display: flex;
  gap: 20px;
}

@media (max-width: 991px) {
  .statistics-grid {
    max-width: 100%;
    margin-top: 40px;
  }

  .statistics-layout {
    flex-direction: column;
  }
}
</style>