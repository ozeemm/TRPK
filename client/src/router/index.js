import { createRouter, createWebHistory } from 'vue-router'

import LoginView from "@/views/LoginView.vue";
import ProfileView from '@/views/ProfileView.vue';
import NewReservationView from '@/views/NewReservationView.vue';
import ReservationsHistoryView from '@/views/ReservationsHistoryView.vue';

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [{
        path: "/login",
        name: "LoginView",
        component: LoginView
    },{
        path: "/profile",
        name: "ProfileView",
        component: ProfileView
    },{
        path: "/reservations/new",
        name: "NewReservationView",
        component: NewReservationView
    },{
        path: "/reservations/history",
        name: "ReservationsHistoryView",
        component: ReservationsHistoryView
    }]
})

export default router