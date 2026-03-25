<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Cookies from 'js-cookie'

const reservations = ref({
  Confirmation: [],
  Reserved: [],
  Past: []
})
const loading = ref(false)
const error = ref(null)
const actionLoading = ref({})

onMounted(async () => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get('csrftoken')
  fetchReservations()
})

async function fetchReservations() {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get('/api/reservations/')
    reservations.value = response.data
  } catch (err) {
    error.value = 'Ошибка загрузки записей'
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function confirmReservation(id) {
  actionLoading.value[id] = true
  try {
    await axios.post(`/api/reservations/${id}/confirm/`)
    await fetchReservations()
  } catch (err) {
    error.value = err.response?.data?.error || 'Ошибка подтверждения'
    console.error(err)
  } finally {
    actionLoading.value[id] = false
  }
}

async function cancelReservation(id) {
  actionLoading.value[id] = true
  try {
    await axios.post(`/api/reservations/${id}/cancel/`)
    await fetchReservations()
  } catch (err) {
    error.value = err.response?.data?.error || 'Ошибка отмены'
    console.error(err)
  } finally {
    actionLoading.value[id] = false
  }
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

function formatWeekday(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', { weekday: 'long' })
}

function getStatusBadgeClass(status) {
  const classes = {
    [ReservationStatus.CONFIRMED]: 'bg-success',
    [ReservationStatus.AWAITING_CONFIRMATION]: 'bg-warning text-dark',
    [ReservationStatus.RESERVED]: 'bg-primary',
    [ReservationStatus.CANCELLED]: 'bg-secondary',
    [ReservationStatus.COMPLETED]: 'bg-info text-dark'
  }
  return classes[status] || 'bg-secondary'
}

const ReservationStatus = {
  CONFIRMED: 'Confirmed',
  AWAITING_CONFIRMATION: 'Awaiting Confirmation',
  RESERVED: 'Reserved',
  CANCELLED: 'Cancelled',
  COMPLETED: 'Completed'
}

function getStatusLabel(status) {
  const labels = {
    [ReservationStatus.CONFIRMED]: 'Подтверждена',
    [ReservationStatus.AWAITING_CONFIRMATION]: 'Ожидает подтверждения',
    [ReservationStatus.RESERVED]: 'Забронирована',
    [ReservationStatus.CANCELLED]: 'Отменена',
    [ReservationStatus.COMPLETED]: 'Завершена'
  }
  return labels[status] || status
}
</script>

<template>
  <div class="reservations-history-container">
    <h2 class="page-title">История записей</h2>

    <div v-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle"></i> {{ error }}
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
    </div>

    <div v-else class="reservations-container">
      <!-- Блок 1: Требующие подтверждения и подтверждённые -->
      <section class="reservation-section confirmation-section">
        <div class="section-header">
          <h3>
            <i class="bi bi-check-circle"></i>
            Подтверждение и подтверждённые
          </h3>
          <span class="count-badge">{{ reservations.Confirmation.length }}</span>
        </div>

        <div v-if="reservations.Confirmation.length === 0" class="no-items">
          Нет записей в этом блоке
        </div>

        <div v-else class="reservations-list">
          <div
            v-for="reservation in reservations.Confirmation"
            :key="reservation.id"
            class="reservation-card"
          >
            <div class="card-top">
              <span class="status-badge" :class="getStatusBadgeClass(reservation.status)">
                {{ getStatusLabel(reservation.status) }}
              </span>
              <span class="reservation-date">
                {{ formatWeekday(reservation.time_slot.reservation_date) }}, {{ formatDate(reservation.time_slot.reservation_date) }}
              </span>
            </div>

            <div class="card-body">
              <div class="info-row">
                <i class="bi bi-clock"></i>
                <span>{{ reservation.time_slot.reservation_time_start }} - {{ reservation.time_slot.reservation_time_end }}</span>
              </div>
              <div class="info-row">
                <i class="bi bi-person-badge"></i>
                <span>{{ reservation.time_slot.doctor.surname }} {{ reservation.time_slot.doctor.name }} {{ reservation.time_slot.doctor.lastname }}</span>
              </div>
              <div class="info-row">
                <i class="bi bi-star"></i>
                <span>{{ reservation.time_slot.doctor.speciality }}</span>
              </div>
            </div>

            <div class="card-actions">
              <button
                v-if="reservation.status === ReservationStatus.AWAITING_CONFIRMATION"
                @click="confirmReservation(reservation.id)"
                class="btn btn-success btn-sm"
                :disabled="actionLoading[reservation.id]"
              >
                <span v-if="actionLoading[reservation.id]" class="spinner-border spinner-border-sm"></span>
                Подтвердить
              </button>
              <button
                v-if="reservation.status === ReservationStatus.AWAITING_CONFIRMATION || 
                      reservation.status === ReservationStatus.RESERVED"
                @click="cancelReservation(reservation.id)"
                class="btn btn-outline-danger btn-sm"
                :disabled="actionLoading[reservation.id]"
              >
                Отменить
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Блок 2: Забронированные (будущие) -->
      <section class="reservation-section reserved-section">
        <div class="section-header">
          <h3>
            <i class="bi bi-calendar-check"></i>
            Забронированные
          </h3>
          <span class="count-badge">{{ reservations.Reserved.length }}</span>
        </div>

        <div v-if="reservations.Reserved.length === 0" class="no-items">
          Нет забронированных записей
        </div>

        <div v-else class="reservations-list">
          <div
            v-for="reservation in reservations.Reserved"
            :key="reservation.id"
            class="reservation-card"
          >
            <div class="card-top">
              <span class="status-badge" :class="getStatusBadgeClass(reservation.status)">
                {{ getStatusLabel(reservation.status) }}
              </span>
              <span class="reservation-date">
                {{ formatWeekday(reservation.time_slot.reservation_date) }}, {{ formatDate(reservation.time_slot.reservation_date) }}
              </span>
            </div>

            <div class="card-body">
              <div class="info-row">
                <i class="bi bi-clock"></i>
                <span>{{ reservation.time_slot.reservation_time_start }} - {{ reservation.time_slot.reservation_time_end }}</span>
              </div>
              <div class="info-row">
                <i class="bi bi-person-badge"></i>
                <span>{{ reservation.time_slot.doctor.surname }} {{ reservation.time_slot.doctor.name }} {{ reservation.time_slot.doctor.lastname }}</span>
              </div>
              <div class="info-row">
                <i class="bi bi-star"></i>
                <span>{{ reservation.time_slot.doctor.speciality }}</span>
              </div>
            </div>

            <div class="card-actions">
              <button
                @click="cancelReservation(reservation.id)"
                class="btn btn-outline-danger btn-sm"
                :disabled="actionLoading[reservation.id]"
              >
                Отменить
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Блок 3: Прошлые -->
      <section class="reservation-section past-section">
        <div class="section-header">
          <h3>
            <i class="bi bi-archive"></i>
            Прошлые записи
          </h3>
          <span class="count-badge">{{ reservations.Past.length }}</span>
        </div>

        <div v-if="reservations.Past.length === 0" class="no-items">
          Нет прошлых записей
        </div>

        <div v-else class="reservations-list">
          <div
            v-for="reservation in reservations.Past"
            :key="reservation.id"
            class="reservation-card"
          >
            <div class="card-top">
              <span class="status-badge" :class="getStatusBadgeClass(reservation.status)">
                {{ getStatusLabel(reservation.status) }}
              </span>
              <span class="reservation-date">
                {{ formatWeekday(reservation.time_slot.reservation_date) }}, {{ formatDate(reservation.time_slot.reservation_date) }}
              </span>
            </div>

            <div class="card-body">
              <div class="info-row">
                <i class="bi bi-clock"></i>
                <span>{{ reservation.time_slot.reservation_time_start }} - {{ reservation.time_slot.reservation_time_end }}</span>
              </div>
              <div class="info-row">
                <i class="bi bi-person-badge"></i>
                <span>{{ reservation.time_slot.doctor.surname }} {{ reservation.time_slot.doctor.name }} {{ reservation.time_slot.doctor.lastname }}</span>
              </div>
              <div class="info-row">
                <i class="bi bi-star"></i>
                <span>{{ reservation.time_slot.doctor.speciality }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.reservations-history-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  margin-bottom: 24px;
  color: #333;
}

.alert {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 40px;
}

.reservations-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.reservation-section {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.count-badge {
  background: rgba(0, 0, 0, 0.1);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

/* Цвета секций */
.confirmation-section {
  border-left: 4px solid #667eea;
}

.confirmation-section .section-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.confirmation-section .section-header h3 {
  color: white;
}

.reserved-section {
  border-left: 4px solid #11998e;
}

.reserved-section .section-header {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
}

.reserved-section .section-header h3 {
  color: white;
}

.past-section {
  border-left: 4px solid #868f96;
}

.past-section .section-header {
  background: linear-gradient(135deg, #868f96 0%, #596164 100%);
  color: white;
}

.past-section .section-header h3 {
  color: white;
}

.no-items {
  text-align: center;
  color: #6c757d;
  padding: 40px 20px;
}

.reservations-list {
  padding: 16px;
}

.reservation-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  margin-bottom: 12px;
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.reservation-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.reservation-card:last-child {
  margin-bottom: 0;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.reservation-date {
  font-size: 13px;
  color: #6c757d;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  color: #495057;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row i {
  color: #007bff;
  width: 16px;
}

.card-actions {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #e9ecef;
  background: #fafbfc;
}

.btn {
  flex: 1;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}
</style>
