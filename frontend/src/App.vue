<template>
  <div class="app-shell">
    <header class="app-header">
      <div class="header-content">
        <router-link to="/" class="logo">Storyloom</router-link>
        <div class="header-right">
          <nav class="nav-links" v-if="route.name !== 'home'">
            <router-link to="/" class="nav-link">Projects</router-link>
          </nav>
          <ThemeToggle />
        </div>
      </div>
    </header>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import ThemeToggle from '@/components/ThemeToggle.vue'
const route = useRoute()
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  border-bottom: 1px solid var(--border);
  background: var(--header-bg);
  backdrop-filter: blur(12px);
  position: sticky;
  top: 0;
  z-index: 100;
  transition: background 0.3s ease, border-color 0.3s ease;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.logo {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: -0.02em;
  text-decoration: none;
  position: relative;
}

.logo::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, var(--accent), transparent);
}

.nav-links {
  display: flex;
  gap: 1.5rem;
}

.nav-link {
  font-size: 0.9rem;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s;
  font-weight: 400;
}

.nav-link:hover {
  color: var(--accent);
}

.app-main {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
}
</style>
