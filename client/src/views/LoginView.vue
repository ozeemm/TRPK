<script setup>
import { ref, onBeforeMount } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useRouter } from 'vue-router';
import { useUserStore } from '../../stores/userStore';
import { storeToRefs } from 'pinia';

const userStore = useUserStore()
const userInfo = storeToRefs(userStore)

const router = useRouter();

const phone = ref('');
const password = ref('');

async function login(){
    try {
        const response = await axios.post('/api/user/login/', {
            phone: phone.value,
            password: password.value
        })

        if(response.status === 200) {
            await userStore.getInfo()
            router.push("/profile")
        } else if(response.status === 401) {
            alert("Ошибка: неверный номер телефона или пароль")
        } else {
            alert("Ошибка авторизации")
        }
    } catch (error) {
        if(error.response?.status === 401) {
            alert("Ошибка: неверный номер телефона или пароль")
        } else {
            alert("Ошибка авторизации")
        }
    }
}

onBeforeMount(async () => {
    axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken")
})
</script>

<template>
    <div class="container d-flex justify-content-center align-items-center min-vh-100">
        <div class="card shadow-sm" style="width: 100%; max-width: 400px;">
            <div class="card-body p-4">
                <h2 class="text-center mb-4">Вход</h2>
                
                <form @submit.prevent="login">
                    <div class="mb-3">
                        <label for="phone" class="form-label">Номер телефона</label>
                        <input 
                            type="tel" 
                            class="form-control" 
                            id="phone" 
                            placeholder="00000000000"
                            v-model="phone"
                            maxlength="11"
                        >
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Пароль</label>
                        <input 
                            type="password" 
                            class="form-control" 
                            id="password" 
                            placeholder="Введите пароль"
                            v-model="password"
                        >
                    </div>
                    <button type="submit" class="btn btn-primary w-100">
                        Войти
                    </button>
                </form>
            </div>
        </div>
    </div>
</template>
