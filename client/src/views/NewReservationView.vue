<script setup>
import { ref, computed, onBeforeMount } from 'vue'
import axios from 'axios'
import Cookies from 'js-cookie'

const doctorsBySpeciality = ref({})
const specialities = ref([])
const selectedSpeciality = ref(null)
const selectedDoctor = ref(null)
const timeSlots = ref([])
const selectedSlot = ref(null)
const loadingDoctors = ref(false)
const loadingSlots = ref(false)
const submitting = ref(false)
const error = ref(null)
const success = ref(false)

// Загрузка врачей при монтировании
async function fetchDoctors() {
    loadingDoctors.value = true
    try {
        const response = await axios.get('/api/doctors/')
        doctorsBySpeciality.value = response.data
        specialities.value = Object.keys(response.data)
    } catch (err) {
        error.value = 'Ошибка загрузки врачей'
        console.error(err)
    } finally {
        loadingDoctors.value = false
    }
}

// Врачи выбранной специальности
const availableDoctors = computed(() => {
  if (!selectedSpeciality.value) return []
  return doctorsBySpeciality.value[selectedSpeciality.value] || []
})

// Сброс врача при смене специальности
function onSpecialityChange() {
  selectedDoctor.value = null
  timeSlots.value = []
  selectedSlot.value = null
}

// Загрузка слотов при выборе врача
async function onDoctorChange() {
  if (!selectedDoctor.value) {
    timeSlots.value = []
    return
  }

  loadingSlots.value = true
  try {
    const response = await axios.get(`/api/doctorschedule/${selectedDoctor.value.id}/`)
    timeSlots.value = response.data
    selectedSlot.value = null
  } catch (err) {
    error.value = 'Ошибка загрузки расписания'
    console.error(err)
  } finally {
    loadingSlots.value = false
  }
}

// Группировка слотов по датам
const slotsByDate = computed(() => {
  const grouped = {}
  timeSlots.value.forEach(slot => {
    if (!grouped[slot.reservation_date]) {
      grouped[slot.reservation_date] = []
    }
    grouped[slot.reservation_date].push(slot)
  })
  return grouped
})

// Создание записи
async function submitReservation() {
  if (!selectedSlot.value) {
    error.value = 'Выберите временной слот'
    return
  }

  submitting.value = true
  error.value = null
  success.value = false

  try {
    await axios.post('/api/reservations/', {
      time_slot: selectedSlot.value.id
    })
    success.value = true
    // Сброс формы
    selectedSlot.value = null
    selectedDoctor.value = null
    selectedSpeciality.value = null
    timeSlots.value = []
  } catch (err) {
    // Обработка ошибок от Django REST Framework
    const data = err.response?.data
    console.error('Ошибка API:', data)
    
    if (data?.error) {
      error.value = data.error
    } else if (data?.non_field_errors) {
      // Общие ошибки (например, "У вас уже есть 2 активные записи")
      error.value = Array.isArray(data.non_field_errors)
        ? data.non_field_errors.join(', ')
        : data.non_field_errors
    } else if (data?.time_slot) {
      // Ошибки валидации поля time_slot (массив сообщений)
      error.value = Array.isArray(data.time_slot)
        ? data.time_slot.join(', ')
        : data.time_slot
    } else {
      error.value = 'Ошибка создания записи'
    }
    console.error(err)
  } finally {
    submitting.value = false
  }
}

onBeforeMount(async () => {
    axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken")
    fetchDoctors()
})
</script>

<template>
  <div class="new-reservation-container">
    <h2 class="page-title">Запись к врачу</h2>

    <!-- Сообщение об успехе -->
    <div v-if="success" class="alert alert-success">
      <i class="bi bi-check-circle"></i> Запись успешно создана!
    </div>

    <!-- Сообщение об ошибке -->
    <div v-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle"></i> {{ error }}
    </div>

    <!-- Форма записи -->
    <div class="reservation-form">
      <!-- Выбор специальности -->
      <div class="form-group">
        <label for="speciality" class="form-label">Специальность врача</label>
        <select
          id="speciality"
          v-model="selectedSpeciality"
          @change="onSpecialityChange"
          class="form-select"
          :disabled="loadingDoctors"
        >
          <option value="" disabled>Выберите специальность</option>
          <option
            v-for="speciality in specialities"
            :key="speciality"
            :value="speciality"
          >
            {{ speciality }}
          </option>
        </select>
      </div>

      <!-- Выбор врача -->
      <div class="form-group">
        <label for="doctor" class="form-label">Врач</label>
        <select
          id="doctor"
          v-model="selectedDoctor"
          @change="onDoctorChange"
          class="form-select"
          :disabled="!selectedSpeciality || loadingSlots"
        >
          <option value="" disabled>Выберите врача</option>
          <option
            v-for="doctor in availableDoctors"
            :key="doctor.id"
            :value="doctor"
          >
            {{ doctor.surname }} {{ doctor.name }} {{ doctor.lastname }}
          </option>
        </select>
      </div>

      <!-- Временные слоты -->
      <div v-if="selectedDoctor" class="time-slots-section">
        <h3 class="slots-title">Доступные слоты</h3>

        <div v-if="loadingSlots" class="loading">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Загрузка...</span>
          </div>
        </div>

        <div
          v-else-if="Object.keys(slotsByDate).length === 0"
          class="no-slots"
        >
          Нет доступных слотов на ближайшие 2 недели
        </div>

        <div v-else class="dates-container">
          <div
            v-for="(slots, date) in slotsByDate"
            :key="date"
            class="date-group"
          >
            <h4 class="date-label">{{ date }}</h4>
            <div class="slots-grid">
              <button
                v-for="slot in slots"
                :key="slot.id"
                @click="selectedSlot = slot"
                class="slot-btn"
                :class="{
                  'selected': selectedSlot?.id === slot.id,
                  'disabled': slot.is_reserved || !slot.is_reservable
                }"
                :disabled="slot.is_reserved || !slot.is_reservable"
              >
                {{ slot.reservation_time_start }} - {{ slot.reservation_time_end }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Кнопка создания записи -->
      <button
        v-if="selectedSlot"
        @click="submitReservation"
        class="btn btn-primary submit-btn"
        :disabled="submitting"
      >
        <span v-if="submitting" class="spinner-border spinner-border-sm"></span>
        {{ submitting ? 'Создание...' : 'Записаться' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.new-reservation-container {
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
  display: flex;
  align-items: center;
  gap: 8px;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.reservation-form {
  background: #fff;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #495057;
}

.form-select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 16px;
  background-color: #fff;
}

.form-select:disabled {
  background-color: #e9ecef;
  cursor: not-allowed;
}

.time-slots-section {
  margin-top: 24px;
}

.slots-title {
  font-size: 18px;
  margin-bottom: 16px;
  color: #333;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 40px;
}

.no-slots {
  text-align: center;
  color: #6c757d;
  padding: 40px;
  background: #f8f9fa;
  border-radius: 8px;
}

.dates-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.date-group {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
}

.date-label {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #495057;
  text-transform: capitalize;
}

.slots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
}

.slot-btn {
  padding: 10px;
  border: 2px solid #007bff;
  background: #fff;
  color: #007bff;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.slot-btn:hover:not(.disabled) {
  background: #007bff;
  color: #fff;
}

.slot-btn.selected {
  background: #007bff;
  color: #fff;
}

.slot-btn.disabled {
  border-color: #dee2e6;
  color: #adb5bd;
  cursor: not-allowed;
  background: #f8f9fa;
}

.submit-btn {
  width: 100%;
  margin-top: 24px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
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