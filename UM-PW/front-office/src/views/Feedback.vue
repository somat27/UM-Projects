<template>
  <div class="feedback-page">
    <Header />
    <PlatformRating />
    <Footer />
  </div>
</template>

<script>
import Header from "@/layouts/Header.vue";
import PlatformRating from "@/components/Feedback/FeedbackForm.vue";
import Footer from "@/layouts/Footer.vue";

export default {
  name: "FeedbackPage",
  components: {
    Header,
    PlatformRating,
    Footer,
  },
};
</script>

<style scoped>
.feedback-page {
  font-family: "Inter", sans-serif;
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
