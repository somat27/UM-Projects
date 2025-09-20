<template>
  <div class="help-page">
    <Header />
    <StepGuide />
    <Footer />
  </div>
</template>

<script>
import Header from "@/layouts/Header.vue";
import StepGuide from "@/components/Help/StepGuide.vue";
import Footer from "@/layouts/Footer.vue";

export default {
  name: "HelpPage",
  components: {
    Header,
    StepGuide,
    Footer,
  },
};
</script>

<style scoped>
.help-page {
  font-family: "Inter", sans-serif;
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
