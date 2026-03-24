<script setup>
import { computed, onBeforeMount } from 'vue';
import { useRoute } from 'vue-router';
import Cookies from 'js-cookie';
import axios from 'axios';
import Navbar from './components/Navbar.vue';

const route = useRoute();

const showNavbar = computed(() => {
    return route.name !== 'LoginView';
});

onBeforeMount(async () => {
    axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken")
})
</script>

<template>
    <div>
        <Navbar v-if="showNavbar" />
        <router-view class="mt-3"/>
    </div>
</template>

<style scoped>
</style>
