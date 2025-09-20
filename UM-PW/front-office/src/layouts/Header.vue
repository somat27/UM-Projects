<template>
  <header class="site-header" :class="{ scrolled: hasScrolled }">
    <router-link to="/" class="logo-container">
      <img src="@/assets/logo.jpg" alt="Logo" class="logo" />
    </router-link>

    <nav class="navigation desktop-nav">
      <router-link to="/ocorrencias" class="nav-link">Ocorrências</router-link>
      <router-link to="/mapa" class="nav-link">Mapa</router-link>
    </nav>

    <button
      class="mobile-menu-button"
      @click="toggleMobileMenu"
      aria-label="Menu"
    >
      <span class="hamburger-line"></span>
      <span class="hamburger-line"></span>
      <span class="hamburger-line"></span>
    </button>

    <div class="mobile-nav" :class="{ active: mobileMenuOpen }">
      <div class="mobile-nav-content">
        <router-link
          to="/ocorrencias"
          class="mobile-nav-link"
          @click="closeMobileMenu"
          >Ocorrências</router-link
        >
        <router-link to="/mapa" class="mobile-nav-link" @click="closeMobileMenu"
          >Mapa</router-link
        >
      </div>
    </div>
  </header>
</template>

<script>
export default {
  name: "AppHeader",
  data() {
    return {
      hasScrolled: false,
      mobileMenuOpen: false,
    };
  },
  mounted() {
    window.addEventListener("scroll", this.handleScroll);
    window.addEventListener("resize", this.handleResize);

    const navLinks = document.querySelectorAll(".nav-link");
    navLinks.forEach((link, index) => {
      setTimeout(() => {
        link.classList.add("visible");
      }, 200 * (index + 1));
    });

    setTimeout(() => {
      const logo = document.querySelector(".logo-container");
      if (logo) logo.classList.add("visible");
    }, 100);
  },
  beforeUnmount() {
    window.removeEventListener("scroll", this.handleScroll);
    window.removeEventListener("resize", this.handleResize);
  },
  methods: {
    handleScroll() {
      this.hasScrolled = window.scrollY > 20;
    },
    toggleMobileMenu() {
      this.mobileMenuOpen = !this.mobileMenuOpen;

      if (this.mobileMenuOpen) {
        document.body.style.overflow = "hidden";
      } else {
        document.body.style.overflow = "";
      }
    },
    closeMobileMenu() {
      this.mobileMenuOpen = false;
      document.body.style.overflow = "";
    },
    handleResize() {
      if (window.innerWidth > 768 && this.mobileMenuOpen) {
        this.closeMobileMenu();
      }
    },
  },
};
</script>

<style scoped>
.site-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  height: 86px;
  background-color: #204c6d;
  z-index: 1000;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.site-header.scrolled {
  height: 70px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

body {
  padding-top: 86px;
}

/* Logo styles */
.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  margin-left: 60px;
  opacity: 0;
  transform: translateY(-10px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.logo-container.visible {
  opacity: 1;
  transform: translateY(0);
}

.logo {
  max-height: 100%;
  max-width: 150px;
  width: auto;
  height: auto;
  object-fit: contain;
  transition: all 0.3s ease;
  transform: scale(1.5);
}

.site-header.scrolled .logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.site-header.scrolled .logo {
  max-height: 100%;
  max-width: 120px;
}

.logo-container:hover .logo {
  transform: scale(1.05);
}

/* Navigation styles */
.navigation {
  display: flex;
  gap: 96px;
  margin-right: 92px;
}

.nav-link {
  color: #fff;
  font-size: 25px;
  position: relative;
  opacity: 0;
  transform: translateY(-10px);
  transition: transform 0.3s ease, opacity 0.5s ease, color 0.3s ease;
  text-decoration: none;
}

.nav-link.visible {
  opacity: 1;
  transform: translateY(0);
}

.nav-link:hover {
  color: #e6f2ff;
  transform: translateY(-2px);
}

.nav-link::after {
  content: "";
  position: absolute;
  width: 100%;
  height: 2px;
  bottom: -4px;
  left: 0;
  background-color: #fff;
  transform: scaleX(0);
  transition: transform 0.3s ease;
  transform-origin: bottom right;
}

.nav-link:hover::after {
  transform: scaleX(1);
  transform-origin: bottom left;
}

/* Mobile menu styles */
.mobile-menu-button {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 10px;
  margin-right: 20px;
  z-index: 1001;
}

.hamburger-line {
  display: block;
  width: 25px;
  height: 3px;
  margin: 5px auto;
  background-color: #fff;
  transition: all 0.3s ease-in-out;
}

.mobile-nav {
  position: fixed;
  top: 0;
  right: -100%;
  width: 100%;
  height: 100vh;
  background-color: #204c6d;
  z-index: 999;
  overflow-y: auto;
  transition: right 0.3s ease-in-out;
}

.mobile-nav.active {
  right: 0;
}

.mobile-nav-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.mobile-nav-link {
  color: #fff;
  font-size: 28px;
  margin: 15px 0;
  text-decoration: none;
  position: relative;
  transition: all 0.3s ease;
}

.mobile-nav-link:hover {
  color: #e6f2ff;
}

.mobile-nav-link::after {
  content: "";
  position: absolute;
  width: 100%;
  height: 2px;
  bottom: -4px;
  left: 0;
  background-color: #fff;
  transform: scaleX(0);
  transition: transform 0.3s ease;
  transform-origin: bottom right;
}

.mobile-nav-link:hover::after {
  transform: scaleX(1);
  transform-origin: bottom left;
}

/* Animations */
@keyframes slideInFromTop {
  0% {
    transform: translateY(-100%);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

.site-header {
  animation: slideInFromTop 0.5s ease-out forwards;
}

/* Responsive layouts */
@media (max-width: 991px) {
  .navigation {
    gap: 48px;
    margin-right: 48px;
  }

  .logo-container {
    margin-left: 30px;
  }

  .nav-link {
    font-size: 22px;
  }
}

@media (max-width: 768px) {
  .desktop-nav {
    display: none;
  }

  .mobile-menu-button {
    display: block;
  }

  .logo-container {
    margin-left: 20px;
  }

  .logo {
    max-width: 130px;
    transform: scale(1.2);
  }

  .site-header.scrolled .logo {
    max-width: 110px;
  }

  .mobile-menu-button.active .hamburger-line:nth-child(1) {
    transform: translateY(8px) rotate(45deg);
  }

  .mobile-menu-button.active .hamburger-line:nth-child(2) {
    opacity: 0;
  }

  .mobile-menu-button.active .hamburger-line:nth-child(3) {
    transform: translateY(-8px) rotate(-45deg);
  }
}

@media (max-width: 480px) {
  .site-header {
    height: 70px;
    padding: 8px 0;
  }

  .site-header.scrolled {
    height: 60px;
  }

  body {
    padding-top: 70px;
  }

  .logo {
    max-width: 110px;
    transform: scale(1);
  }

  .site-header.scrolled .logo {
    max-width: 100px;
  }
}
</style>
