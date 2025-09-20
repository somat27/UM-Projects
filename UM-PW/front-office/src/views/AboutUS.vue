<template>
  <main class="page-container">
    <Header />
    <AboutContent />
    <Footer />
  </main>
</template>

<script>
import Header from "@/layouts/Header.vue";
import Footer from "@/layouts/Footer.vue";
import AboutContent from "@/components/AboutUS/AboutContent.vue";

export default {
  name: "AboutUS",
  components: {
    Header,
    AboutContent,
    Footer,
  },
};
</script>

<style scoped>
.page-container {
  width: 100%;
  min-height: 100vh;
  background-color: #fff;
  display: flex;
  flex-direction: column;
}
</style>
