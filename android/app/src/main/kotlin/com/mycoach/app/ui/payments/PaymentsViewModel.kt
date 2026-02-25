package com.mycoach.app.ui.payments

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.mycoach.app.api.ApiClient
import com.mycoach.app.models.Payment
import com.mycoach.app.models.PaymentRequest
import kotlinx.coroutines.launch

class PaymentsViewModel : ViewModel() {

    private val _payments = MutableLiveData<List<Payment>>()
    val payments: LiveData<List<Payment>> = _payments

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    private val _loading = MutableLiveData(false)
    val loading: LiveData<Boolean> = _loading

    fun load(clientId: Int? = null) {
        viewModelScope.launch {
            _loading.value = true
            try {
                _payments.value = ApiClient.service.getPayments(clientId)
                _error.value = null
            } catch (e: Exception) {
                _error.value = e.message
            } finally {
                _loading.value = false
            }
        }
    }

    fun create(request: PaymentRequest) {
        viewModelScope.launch {
            try {
                ApiClient.service.createPayment(request)
                load()
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }

    fun delete(id: Int) {
        viewModelScope.launch {
            try {
                ApiClient.service.deletePayment(id)
                load()
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }
}
