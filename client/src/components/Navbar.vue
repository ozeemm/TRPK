<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import Cookies from 'js-cookie'

const showNotifications = ref(false)

// const notifications = ref([
//     { id: 1, message: 'Приём назначен на 20.03.2026 в 14:00', is_viewed: false, sending_datetime: new Date(Date.now() - 5 * 60 * 1000).toISOString() },
//     { id: 2, message: 'Напоминание: визит к врачу завтра', is_viewed: false, sending_datetime: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString() },
//     { id: 3, message: 'Результаты анализов готовы', is_viewed: true, sending_datetime: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString() }
// ])
const notifications = ref([])

const unreadCount = computed(() => notifications.value.filter(n => !n.is_viewed).length)

async function fetchNotifications(){
    const response = await axios.get('/api/notifications/')
    notifications.value = response.data
}

function formatTimeAgo(dateString) {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) {
        return 'только что'
    } else if (diffMins < 60) {
        return `${diffMins} мин. назад`
    } else if (diffHours < 24) {
        return `${diffHours} ч. назад`
    } else {
        return `${diffDays} дн. назад`
    }
}

async function toggleNotifications() {
    showNotifications.value = !showNotifications.value
    // Помечаем все уведомления как прочитанные при открытии
    if (showNotifications.value) {
        const notifications_to_read = []

        notifications.value.forEach(n => {
            if(!n.is_viewed)
                notifications_to_read.push(n.id)
            n.is_viewed = true
        })

        if(notifications_to_read.length > 0){
            const response = await axios.post('/api/notifications/read/', {
                notifications: notifications_to_read
            })
        }
    }
}

onMounted(async () => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get('csrftoken')
  fetchNotifications()
})
</script>

<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">Dental Clinic</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <router-link class="nav-link" to="/profile">Профиль</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" to="/reservations/new">Записаться</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" to="/reservations/history">Мои записи</router-link>
                    </li>
                </ul>
                <div class="d-flex align-items-center position-relative">
                    <div class="dropdown">
                        <button
                            class="btn btn-link text-white position-relative"
                            @click="toggleNotifications"
                        >
                            <i class="bi bi-bell" style="font-size: 1.5rem;"></i>
                            <span
                                v-if="unreadCount > 0"
                                class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
                            >
                                {{ unreadCount }}
                            </span>
                        </button>
                        <div
                            v-if="showNotifications"
                            class="dropdown-menu show notifications-dropdown"
                            style="min-width: 300px;"
                        >
                            <h6 class="dropdown-header">Уведомления</h6>
                            <div v-if="notifications.length === 0" class="dropdown-item text-muted">
                                Нет уведомлений
                            </div>
                            <a
                                v-for="notification in notifications"
                                :key="notification.id"
                                class="dropdown-item"
                                :class="{ 'fw-bold': !notification.is_viewed }"
                            >
                                <div class="d-flex align-items-start">
                                    <i class="bi me-2" :class="notification.is_viewed ? 'bi-check2' : 'bi-circle-fill'" style="font-size: 0.5rem; margin-top: 4px;"></i>
                                    <div class="flex-grow-1">
                                        <div>{{ notification.message }}</div>
                                        <small class="text-muted">{{ formatTimeAgo(notification.sending_datetime) }}</small>
                                    </div>
                                </div>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </nav>
</template>

<style scoped>
.notifications-dropdown {
    position: absolute;
    right: 0;
    top: 100%;
    margin-top: 0.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border: none;
}
</style>
