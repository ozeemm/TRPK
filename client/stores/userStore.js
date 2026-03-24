import { ref } from "vue";
import axios from "axios";
import { defineStore } from "pinia";

export const useUserStore = defineStore("UserStore", () => {
    const isAuthenticated = ref(false)
    const surname = ref()
    const name = ref()
    const lastname = ref()
    const phone = ref()
    const birthday = ref()

    async function getInfo(){
        const r = await axios.get(`/api/user/info/`)

        isAuthenticated.value = r.data.is_authenticated
        surname.value = r.data.surname
        name.value = r.data.name
        lastname.value = r.data.lastname
        phone.value = r.data.phone
        birthday.value = r.data.birthday
    }

    getInfo()

    return { 
        isAuthenticated, surname, name, lastname, phone, birthday, 
        getInfo
    }
})