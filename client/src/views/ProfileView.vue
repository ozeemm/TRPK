<script setup>
import { ref, computed, onBeforeMount } from 'vue';
import { useUserStore } from '../../stores/userStore';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Cookies from 'js-cookie';

const router = useRouter();
const userStore = useUserStore()
const userInfo = storeToRefs(userStore)

async function logout(){
    const response = await axios.post('/api/user/logout/')

    if(response.status == 200)
        router.push('/login')
}

const formattedBirthDate = computed(() => {
    if (!userInfo.birthday.value) return '';
    const date = new Date(userInfo.birthday.value);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}.${month}.${year}`;
});

onBeforeMount(async () => {
    axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken")
})
</script>

<template>
    <div class="container-fluid py-5">
        <div class="row justify-content-center">
            <div class="col-md-10 col-lg-8 col-xl-6">
                <div class="card shadow-sm">
                    <div class="card-header text-center py-4">
                        <div class="avatar-placeholder mb-3">
                            <i class="bi bi-person-circle" style="font-size: 5rem;"></i>
                        </div>
                        <h4 class="mb-0">{{ userInfo.surname }} {{ userInfo.name }} {{ userInfo.lastname }}</h4>
                    </div>
                    <div class="card-body p-4">
                        <div class="mb-4">
                            <label class="text-muted small text-uppercase">Номер телефона</label>
                            <p class="mb-0">{{ userInfo.phone }}</p>
                        </div>
                        <hr>
                        <div class="mb-4">
                            <label class="text-muted small text-uppercase">Дата рождения</label>
                            <p class="mb-0">{{ formattedBirthDate }}</p>
                        </div>
                    </div>
                    <div class="card-footer bg-white text-center py-3">
                        <button class="btn btn-outline-danger w-100" @click="logout">
                            <i class="bi bi-box-arrow-right me-2"></i>Выйти
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.avatar-placeholder {
    width: 120px;
    height: 120px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f8f9fa;
    border-radius: 50%;
}

.card-header {
    background-color: #f8f9fa;
    border-bottom: 2px solid #e9ecef;
}
</style>
