<template>
  <main class="report-map">
    <Header />
    <ReportForm :defaultCategory="defaultCategory" />
    <Footer />
  </main>
</template>

<script>
import Header from "@/layouts/Header.vue";
import ReportForm from "@/components/Report/ReportForm";
import Footer from "@/layouts/Footer.vue";

export default {
  name: "ReportMap",
  components: {
    Header,
    ReportForm,
    Footer,
  },
  props: {
    defaultCategory: {
      type: String,
      default: "",
    },
  },
};
</script>

<style scoped>
.report-map {
  width: 100%;
}
</style>