<template>
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap"
    rel="stylesheet"
  />
  <div class="occurrences-page">
    <Header />
    <main class="main-content">
      <section class="occurrences-header">
        <h1 class="occurrences-title">Ocorrencias</h1>
        <p class="occurrences-description">
          Aqui podes consultar o estado e os detalhes das ocorrências
        </p>
      </section>
      <OccurrencesTable />
    </main>
    <Footer />
  </div>
</template>

<script>
import Header from "@/layouts/Header.vue";
import OccurrencesTable from "@/components/OcurrencePage/OcurrenceTable.vue";
import Footer from "@/layouts/Footer.vue";

export default {
  name: "OccurrencesPage",
  components: {
    Header,
    OccurrencesTable,
    Footer,
  },
};
</script>

<style scoped>
.occurrences-page {
  font-family: "Inter", sans-serif;
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding-top: 5%;
}

.main-content {
  padding: 0 64px;
  flex: 1;
  background-color: #fff;
  padding-bottom: 5%;
}

@media (max-width: 991px) {
  .main-content {
    padding: 0 32px;
  }
}

@media (max-width: 640px) {
  .main-content {
    padding: 0 16px;
  }
}

.occurrences-header {
  text-align: center;
  padding: 40px 0;
}

.occurrences-title {
  color: #204c6d;
  font-size: 50px;
  font-weight: 700;
  margin-bottom: 11px;
}

@media (max-width: 640px) {
  .occurrences-title {
    font-size: 36px;
  }
}

.occurrences-description {
  color: #000;
  font-size: 25px;
  font-weight: 700;
}

@media (max-width: 640px) {
  .occurrences-description {
    font-size: 20px;
  }
}
</style>
